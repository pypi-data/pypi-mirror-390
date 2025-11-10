# 本代码适用于25年3月的纵缝提取
from typing import Union
import numpy as np
import zelas2.shield as zs
import multiprocessing as mp
import zelas2.Multispectral as zm
from sympy.codegen.ast import Return
from tqdm import tqdm
import cv2
from scipy.spatial.transform import Rotation
import zelas2.RedundancyElimination as zr
from sklearn.neighbors import KDTree  # 添加机器学习的skl.KDT的函数组
from multiprocessing import shared_memory
from sklearn.cluster import DBSCAN
import zelas2.ransac as zR
import zelas2.TheHeartOfTheMilitaryGod as zt
from scipy.spatial.distance import pdist, squareform
from scipy.signal import find_peaks

def find_continuous_segments_numpy(arr):
    """
    找到一维数组中所有连续整数段的起始和终止数，返回 NumPy 数组
    :param arr: 一维整数数组（已排序）
    :return: NumPy 数组，每行为 (起始数, 终止数)
    """
    segments = []  # 存储所有连续段
    start = arr[0]  # 当前连续段的起始数
    for i in range(1, len(arr)):
        if arr[i] != arr[i - 1] + 1:  # 检测中断点
            segments.append((start, arr[i - 1]))  # 保存当前连续段
            start = arr[i]  # 开始新的连续段
    # 添加最后一个连续段
    segments.append((start, arr[-1]))
    # 转换为 NumPy 数组
    return np.array(segments, dtype=int)

def get_ρθ(xz_p, xzr):
    '求每个盾构环的极径差和反正切'
    num_p = len(xz_p)  # 当前截面点数量
    ρ = np.sqrt((xz_p[:,0]-xzr[0])**2+(xz_p[:,1]-xzr[1])**2)-xzr[2]
    θ = np.empty(num_p)
    for i in range(num_p):
        θ[i] = zs.get_angle(xz_p[i,0],xz_p[i,1],xzr[0],xzr[1])
    return np.c_[ρ,θ]

def find_seed(θyρvci,ρ_td,r,cpu=mp.cpu_count(),c_ignore=4):
    '寻找符合纵缝特征的种子点'
    θyρvci_up = θyρvci[θyρvci[:,2]>=ρ_td,:]  # 低于衬砌点的不要
    # 准备工作
    pool = mp.Pool(processes=cpu)  # 开启多进程池，数量为cpu
    c_un = np.unique(θyρvci[:,4])
    num_c = len(np.unique(θyρvci[:,4]))  # 截面数
    # good_index = []
    # 并行计算
    multi_res = pool.starmap_async(find_seed_cs, ((θyρvci,np.uint64(θyρvci_up[θyρvci_up[:,4]==c_un[i],5]),c_un[i],r,c_ignore) for i in
                 tqdm(range(num_c),desc='分配任务寻找种子点',unit='个截面',total=num_c)))
    j = 0
    for res in tqdm(multi_res.get(),total=num_c,desc='输出种子点下标'):
        if j==0:
            good_index = res
        else:
            good_index = np.hstack((good_index, res))
        j += 1
    pool.close()  # 关闭所有进程
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算
    return np.int64(good_index)


def find_seed_cs(θyρvci,id_θyρvci_up_c,c,r,c_ignore=4):
    '''
    寻找单个截面符合纵缝特征的种子点
    θyρvci : 点云信息
    id_θyρvci_up_c ：符合搜索的点云下标
    c ：当前截面
    r :当前截面半径
    c_ignore ：忽略的截面数
    '''
    good_ind = []  # 空下标
    θ_l_td = 0.15 * np.pi * r / 180
    for i in id_θyρvci_up_c:
        if θyρvci[i,3]==0:  # 如果当前点为线特征
            # 找到搜索截面
            θyρ_c_ = θyρvci[θyρvci[:, 4] <= c + c_ignore, :]
            θyρ_c_ = θyρ_c_[θyρ_c_[:, 4] >= c - c_ignore, :]
            # 判断左侧是否有球特征
            θ_l_ = θyρvci[i,0] - θ_l_td  # 左侧角度阈值
            θyρ_l_ = θyρ_c_[θyρ_c_[:, 0] < θyρvci[i, 0], :]
            θyρ_l_ = θyρ_l_[θyρ_l_[:, 0] >= θ_l_, :]
            # 判断右侧是否有球特征
            θ_r_ = θyρvci[i,0] + θ_l_td  # 右侧角度阈值
            θyρ_r_ = θyρ_c_[θyρ_c_[:, 0] > θyρvci[i, 0], :]
            θyρ_r_ = θyρ_r_[θyρ_r_[:, 0] <= θ_r_, :]
            if 2 in θyρ_l_[:, 3] and 2 in θyρ_r_[:, 3]:  # 如果左右都有球特征
                good_ind.append(θyρvci[i,5])  # 作为种子点
    return good_ind

def distance_to_line(point, line):
    """计算点到直线的几何距离"""
    x0, y0 = point
    x1, y1, x2, y2 = line
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    return numerator / denominator if denominator != 0 else 0

def merge_similar_lines(lines, angle_thresh=np.pi / 18, rho_thresh=20):
    """合并相似直线（极坐标参数相近的线段）"""
    merged = []
    for line in lines:
        rho, theta = line_to_polar(line[0])
        found = False
        for m in merged:
            m_rho, m_theta = m[0]
            # 检查角度和距离差异
            if abs(theta - m_theta) < angle_thresh and abs(rho - m_rho) < rho_thresh:
                m[0] = ((m_rho + rho) / 2, (m_theta + theta) / 2)  # 合并平均值
                m[1].append(line)
                found = True
                break
        if not found:
            merged.append([(rho, theta), [line]])

    # 转换回线段格式（取合并后的极坐标生成新线段）
    merged_lines = []
    for m in merged:
        rho, theta = m[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        # 生成足够长的线段（覆盖图像范围）
        scale = 1000
        x1 = int(x0 + scale * (-b))
        y1 = int(y0 + scale * (a))
        x2 = int(x0 - scale * (-b))
        y2 = int(y0 - scale * (a))
        merged_lines.append([x1, y1, x2, y2])

    return merged_lines[:5]  # 最多返回前5条

def find_lines(θy):
    '通过数字图像操作将纵缝找到并返回种子点'
    '0.整理数据'
    θy = θy*100
    θy[:, 0] -= np.min(θy[:, 0])
    θy[:, 1] -= np.min(θy[:, 1])
    θy = np.uint64(θy)
    x_max = np.max(θy[:,0])
    y_max = np.max(θy[:,1]) # 求边界
    print('二维边长',x_max,y_max)
    '1.创建图像'
    img = np.zeros((int(y_max)+1, int(x_max)+1), dtype=np.uint8)
    for x,y in θy:
        img[y, x] = 255
    '''
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    '2.直线检测'
    # 霍夫变换检测直线
    lines = cv2.HoughLinesP(img, rho=1, theta=np.pi / 180, threshold=50, minLineLength=50, maxLineGap=50)  # 检测单位像素、角度、超过像素阈值、最小长度阈值、最大间断阈值
    # --- 提取前5条最长的直线 ---
    detected_lines = []
    if lines is not None:
        lines = lines[:, 0, :]
        # 按线段长度排序（从最长到最短）
        lines = sorted(lines, key=lambda x: np.linalg.norm(x[2:] - x[:2]), reverse=True)[:6]
        detected_lines = lines
    threshold_distance = 2.0  # 点到直线的最大允许距离（根据噪声调整）
    # 初始化：所有点标记为未分配
    assigned = np.zeros(len(θy), dtype=bool)
    line_points_list = []  # 存储每条直线的点
    line_indices_list = []  # 存储每条直线的点索引
    for line in detected_lines:
        distances = np.array([distance_to_line(p, line) for p in θy])
        # 筛选未分配且距离小于阈值的点
        mask = (distances < threshold_distance) & ~assigned
        line_points = θy[mask]
        line_points_list.append(line_points)
        indices = np.where(mask)[0]
        line_indices_list.append(indices)
        assigned |= mask  # 标记已分配的点
    # 合并前5条直线的点
    all_line_points = np.vstack(line_points_list)
    # 分离噪声点
    noise_points = θy[~assigned]
    '''
    # --- 可视化结果 ---
    # 创建彩色图像用于显示
    result_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # 绘制检测到的直线（绿色）
    for line in detected_lines:
        x1, y1, x2, y2 = line
        cv2.line(result_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # 绘制属于直线的点（红色）
    for p in all_line_points:
        cv2.circle(result_img, tuple(p), 2, (0, 0, 255), -1)
    '''
    '''
        # 预定义5种颜色（BGR格式）
    colors = [
        (0, 0, 255),   # 红色
        (0, 255, 0),   # 绿色
        (255, 0, 0),   # 蓝色
        (0, 255, 255), # 黄色
        (255, 0, 255)  # 品红色
    ]
    # 绘制每条直线及其对应的点
    for i, (line, line_points) in enumerate(zip(detected_lines, line_points_list)):
        color = colors[i % len(colors)]  # 循环使用颜色列表
        # 绘制直线
        x1, y1, x2, y2 = line
        cv2.line(result_img, (x1, y1), (x2, y2), color, 2)
    '''
    '''
    # 绘制噪声点（蓝色）
    for p in noise_points:
        cv2.circle(result_img, tuple(p.astype(int)), 2, (255, 0, 0), -1)
    cv2.imshow("Result", result_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    # 去除 line_indices_list 中的空元素
    line_indices_list = [indices for indices in line_indices_list if len(indices) > 0]
    return line_indices_list


def merge_similar_lines(lines, angle_thresh=5, dist_thresh=10):
    """
    合并角度和位置相近的线段
    :param lines: 线段列表，格式为 [[x1,y1,x2,y2], ...]
    :param angle_thresh: 角度差阈值（度）
    :param dist_thresh: 线段中心点距离阈值（像素）
    :return: 合并后的线段列表
    """
    merged = []
    for line in lines:
        x1, y1, x2, y2 = line
        # 计算线段角度（弧度）
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        # 计算线段中心点
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        # 检查是否与已合并线段近似
        found = False
        for m in merged:
            m_angle, m_cx, m_cy = m['angle'], m['cx'], m['cy']
            # 角度差和中心点距离
            angle_diff = abs(angle - m_angle)
            dist = np.sqrt((cx - m_cx) ** 2 + (cy - m_cy) ** 2)

            if angle_diff < angle_thresh and dist < dist_thresh:
                # 合并线段（延长端点）
                m['x1'] = min(m['x1'], x1, x2)
                m['y1'] = min(m['y1'], y1, y2)
                m['x2'] = max(m['x2'], x1, x2)
                m['y2'] = max(m['y2'], y1, y2)
                found = True
                break

        if not found:
            merged.append({
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'angle': angle, 'cx': cx, 'cy': cy
            })
    # 转换为坐标格式
    return [[m['x1'], m['y1'], m['x2'], m['y2']] for m in merged]


def fit_3d_line(points):
    """
    Fit a 3D line to a point cloud using PCA.
    Parameters:
    points (numpy.ndarray): Nx3 array of 3D points.
    Returns:
    tuple: (centroid, direction_vector)
        centroid is a point on the line (numpy.ndarray of shape (3,)),
        direction_vector is the direction vector of the line (numpy.ndarray of shape (3,)).
    """
    # 计算点云的质心
    centroid = np.mean(points, axis=0)
    # 将点云中心化
    centered_points = points - centroid
    # 计算协方差矩阵
    cov_matrix = np.cov(centered_points.T)
    # 计算协方差矩阵的特征值和特征向量
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    # 找到最大特征值对应的特征向量作为方向向量
    direction_vector = eigenvectors[:, np.argmax(eigenvalues)]
    # Centroid (a point on the line): [1.5 1.5 1.5]
    # Direction vector: [0.57735027 0.57735027 0.57735027]
    return centroid, direction_vector


def distance_to_line_3D(points, centroid, direction):
    """
    计算点到三维直线的距离。
    Parameters:
    points (numpy.ndarray): Nx3 的3D点。
    centroid (numpy.ndarray): 直线上的一点，形状为 (3,)。
    direction (numpy.ndarray): 直线的单位方向向量，形状为 (3,)。
    Returns:
    numpy.ndarray: 每个点到直线的距离，形状为 (N,)。
    """
    # 计算点与质心的向量差
    vec = points - centroid
    # 计算叉乘 (支持批量计算)
    cross_product = np.cross(vec, direction)
    # 距离为叉乘的模长
    distances = np.linalg.norm(cross_product, axis=1)
    return distances

def find_CS_25(xyzic,GirthInterval=245,num_cpu=mp.cpu_count(),z_range=1):
    '环缝提取，固定长度版，25年修补版'
    xyzic[:, 3] = zm.normalization(xyzic[:, 3], 255)  # 强度值离散化
    # 计算每个环的平均强度值
    c_un = np.unique(xyzic[:, 4])  # 圆环从小到大排列
    num_C = len(c_un)  # 截面数量
    # 并行计算准备
    tik = zs.cut_down(num_C, num_cpu)  # 分块起止点
    pool = mp.Pool(processes=num_cpu)  # 开启多进程池，数量为cpu
    # 限制参与计算的比例
    z_max = np.max(xyzic[:, 2])
    z_min = np.min(xyzic[:, 2])
    d_z = z_max - z_min
    t_z = z_min + d_z * (1 - z_range)  # 参与统计的阈值
    ps_free = xyzic[xyzic[:, 2] >= t_z, :]  # 参与统计的点云
    i_c = np.empty(num_C)  # 新建一个存储圆环平均强度值的容器
    multi_res = [pool.apply_async(zs.find_cImean_block, args=(ps_free, c_un, tik[i], tik[i + 1])) for i in
                 range(num_cpu)]  # 将每个block需要处理的点云区间发送到每个进程当中
    tik_ = 0  # 计数器
    for res in multi_res:
        i_c[tik[tik_]:tik[tik_ + 1]] = res.get()
        tik_ += 1
    pool.close()  # 禁止进程池再接收任务
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算
    # 后期整理
    i_c = zm.normalization(i_c, 255)  # 均值离散化
    i_c_mean = np.mean(i_c)  # 平均强度值均值
    i_c_std = np.std(i_c)  # 平均强度值方差
    print('截面强度值均值', i_c_mean, '截面强度值标准差', i_c_std)
    # 找到强度值的最低点以及其他的极低点
    id_min = np.argmin(i_c)
    num_CS_0 = int(np.round(num_C / GirthInterval))  # 假想环缝数量
    print('理论的环缝数量为',str(num_CS_0))
    Begin_CS_0 = id_min % GirthInterval  # 假想起始位置
    id_CS_0 = np.arange(Begin_CS_0, num_C, GirthInterval)  # 假想环缝位置
    print('假想环缝位置',c_un[id_CS_0])
    belong_i = 75  # 强度值搜索半径  # 30
    mid_ = 2  # 余量区间 3
    RB_S = np.array(c_un[0])  # 衬砌开始位置
    RB_E = []  # 衬砌结束位置
    c_name_ins = np.empty(num_CS_0)  # 极低值容器
    c_ = []  # 环缝的存储名
    c_id = []  # 环缝的存储下标器
    N = 8  # 环缝间隔
    #   dis_max = i_c_mean - i_c_std * 3  # 最大差值
    for i in range(num_CS_0):
        # 确保索引在有效范围内
        id_start = max(0, id_CS_0[i] - belong_i)
        id_end = min(len(i_c), id_CS_0[i] + belong_i)
        # 求强度值极低点
        id_min_i_ = np.argmin(i_c[id_start:id_end]) + id_start
        c_name_ins[i] = c_un[id_min_i_]  # 强度值极低点位置
        print('修改后的第', i, '个极低值位置为', c_un[id_min_i_])
        # 寻找以强度值为主的开始和结束位置
        id_min = int(c_name_ins[i] - N)
        id_max = int(c_name_ins[i] + N)
        # 添加衬砌表面起止位置
        RB_E = np.append(RB_E, id_min)  # 添加结束位置
        RB_S = np.append(RB_S, id_max)  # 添加起始位置
    RB_E = np.append(RB_E, c_un[-1])  # 结束位置封顶
    for i in range(num_CS_0):
        if i == 0:
            seams_all = np.arange(RB_E[i], RB_S[i + 1])  # IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed
        else:
            seams_all = np.append(seams_all, np.arange(RB_E[i], RB_S[i + 1]))
    c_xyzic = xyzic[np.isin(xyzic[:, 4], seams_all), :]  # 返回xyzic[:, -1]中有c[c_in]的行数
    # 精简衬砌表面
    id_del = np.isin(np.isin(xyzic[:, 4], seams_all), False)  # 除去环缝点云的点云下标
    txti_delC = xyzic[id_del, :]  # 去除环缝的点云

    return  txti_delC, c_xyzic

def fit_3d_circle(xyz):
    '拟合三维圆'
    num, dim = xyz.shape
    # 求解平面法向量
    L1 = np.ones((num, 1))
    A = np.linalg.inv(xyz.T @ xyz) @ xyz.T @ L1
    # 构建矩阵B和向量L2
    B_rows = (num - 1) * num // 2
    B = np.zeros((B_rows, 3))
    L2 = np.zeros(B_rows)
    count = 0
    for i in range(num):
        for j in range(i + 1, num):
            B[count] = xyz[j] - xyz[i]
            L2[count] = 0.5 * (np.sum(xyz[j] ** 2) - np.sum(xyz[i] ** 2))
            count += 1
    # 构造矩阵D和向量L3
    D = np.zeros((4, 4))
    D[0:3, 0:3] = B.T @ B
    D[0:3, 3] = A.flatten()  # 前三行第四列为A
    D[3, 0:3] = A.T  # 第四行前三列为A的转置
    B_transpose_L2 = B.T @ L2
    L3 = np.concatenate([B_transpose_L2, [1]]).reshape(4, 1)
    # 求解圆心坐标C
    C = np.linalg.inv(D.T) @ L3
    C = C[:3].flatten()  # 提取前三个元素作为圆心
    # 计算半径
    distances = np.linalg.norm(xyz - C, axis=1)
    r = np.mean(distances)
    return np.concatenate([C, [r]])

def fit_3d_circle_mp(xyzc,num_thread=mp.cpu_count()):
    '并行拟合三维圆算法'
    c_un = np.unique(xyzc[:,3])  # 截面序列
    num_c = len(c_un)  # 截面数量
    xyzr_all = np.empty([num_c,4])  # 输出容器
    pool = mp.Pool(processes=num_thread)  # 开启多进程池，数量为cpu
    j = 0  # 分块输出计时器
    # 并行计算
    multi_res = pool.starmap_async(fit_3d_circle, ((xyzc[xyzc[:,3]==c_un[i],:3],) for i in
                 tqdm(range(num_c),desc='分配任务拟合单个三维圆参数',unit='个cross-section',total=num_c)))
    for res in tqdm(multi_res.get(), total=num_c, desc='导出单个三维圆参数', unit='个cross-section'):
        xyzr_all[j,:] = res
        j += 1
    pool.close()  # 禁止进程池再接收任务  #Prohibit process pools from receiving tasks again
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算  #After all processes have completed their calculations, exit parallel computing
    return xyzr_all

def STSD_add_C(las,inx_d = 0.006168):
    '对STSD数据集添加截面序列号'
    # 整理基本信息
    xyz = las.xyz
    I = las.intensity
    inx = las.inx
    label = las.classification
    # 人工制作截面序列号
    inx_un = np.unique(inx)
    inx_min = np.min(inx)
    inx_max = np.max(inx)
    inx_range = np.arange(start=inx_min, stop=inx_max + inx_d, step=inx_d)
    k = 0
    xyzicl = np.c_[xyz,I,inx,label]
    for i in inx_range:
        j = i+inx_d
        xyzicl_ = xyzicl[xyzicl[:,4]<j,:]
        xyzicl_ = xyzicl_[xyzicl_[:, 4] >= i, :]
        xyzicl_[:,4] = k
        if k == 0:
            xyzicl_out = xyzicl_
        else:
            xyzicl_out = np.r_[xyzicl_out,xyzicl_]
        k += 1
    return xyzicl_out

def get_nei_dis_mp(xyz,r,tree,dis_all,cpu=mp.cpu_count()-6):
    '求每个点的平均凸起(建议线程数不超过核心数)'
    # 准备工作
    num = len(xyz)
    dis_in = np.empty(num)  # 存储平均突起的容器
    tik = zs.cut_down(num, cpu)  # 并行计算分块
    pool = mp.Pool(processes=cpu)  # 开启多进程池，数量为cpu
    # 开始进行并行计算
    multi_res = [pool.apply_async(get_nei_dis_block, args=(xyz[tik[i]:tik[i + 1],:], dis_all, tree, r)) for i in
                 range(cpu)]  # 将每个block需要处理的点云区间发送到每个进程当中
    tik_ = 0  # 计数器
    for res in multi_res:
        dis_in[tik[tik_]:tik[tik_ + 1]] = res.get()
        print('已完成',str(tik[tik_]),'到',str(tik[tik_+1]))
        tik_ += 1
    pool.close()  # 禁止进程池再接收任务
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算
    return dis_in

def get_nei_dis_block(xyz_,dis_all,tree,r):
    '分块求每个点的平均凸起'
    num_ = len(xyz_)
    dis_in_ = np.zeros(num_)  # 存储平均突起的容器
    for i in tqdm(range(num_)):
        xyz__ = xyz_[i,:]
        indices, dises = tree.query_radius(xyz__.reshape(1, -1), r=r, return_distance=True,
                                           sort_results=True)  # 返回每个点的邻近点下标列表
        indices = indices[0]
        if len(indices) >= 2:
            dis_all_ = dis_all[indices]  # 临近点圆心距  # dis_all是全部的dis_all
            dis_mean = np.mean(dis_all_[1:])  # 当前点平均圆心距
            dis_ = dis_all_[0] - dis_mean  # 求当前点平均突起
            dis_in_[i] = dis_
    return dis_in_

def get_nei_line_density_c(ca_,width):
    '计算截面每个点左右密度差'
    num_ = len(ca_)
    dd_all_ = np.zeros(num_)
    for i in range(num_):
        a_ = ca_[i, 1]
        a_min = a_ - width
        a_max = a_ + width  # 左右角度区间
        count_l = np.sum((ca_[:, 1] > a_min) & (ca_[:, 1] < a_))
        count_r = np.sum((ca_[:, 1] > a_) & (ca_[:, 1] < a_max))  # 左右角度区间点数
        with np.errstate(divide='ignore', invalid='ignore'):
            ratios = np.minimum(count_l, count_r) / np.maximum(count_l, count_r) # 避免除以零的情况
        # 处理NaN和Inf情况（当分母为0时）
        ratios = np.nan_to_num(ratios, nan=0.0, posinf=1.0, neginf=-1.0)
        dd_all_[i] = ratios
    return dd_all_

def get_nei_line_density_mp(ca,width=360/500,cpu=mp.cpu_count()):
    '计算每个点左右密度差(请先对点云按照截面序列号进行排序)'
    # 准备工作
    # num = len(ca)
    # dd_all = np.empty(num)
    # 按照第一列进行排序
    ca = ca[ca[:, 0].argsort()]
    # 统计每个截面的点数
    # unique_sections, section_counts = np.unique(ca[:, 0], return_counts=True)
    unique_sections = np.unique(ca[:, 0])
    num_c = len(unique_sections)
    pool = mp.Pool(processes=cpu)  # 开启多进程池，数量为cpu
    # 开始进行并行计算
    multi_res = pool.starmap_async(get_nei_line_density_c, ((ca[ca[:,0]==unique_sections[i],:], width) for i in
                 tqdm(range(num_c),desc='分配任务给每个截面求左右密度差',unit='cross-sections',total=num_c)))
    j = 0  # 分块输出计时器
    for res in tqdm(multi_res.get(), total=num_c, desc='导出每个点的左右密度差', unit='cross-sections'):
        if j==0:
            dd_all = res
        else:
            dd_all= np.append(dd_all,res)
        j += 1
    pool.close()  # 禁止进程池再接收任务  #Prohibit process pools from receiving tasks again
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算  #After all processes have completed their calculations, exit parallel computing
    return dd_all

def Curvature_r_mp(xyz,r=0.04,cpu=mp.cpu_count()):
    '并行按照球半径计算曲率'
    # 准备工作
    pool = mp.Pool(processes=cpu)  # 开启多进程池，数量为cpu
    num = len(xyz)  # 返回点云数量
    # start, end = block(num, cpu)  # 返回每个block的起始点云下标和终止点云下标
    tik = zr.cut_down(num, cpu)  # 去除bug后的分块函数
    tree = KDTree(xyz)  # 创建树
    j = 0  # 分块输出计数器
    curvature_all = np.empty(shape=len(xyz))  # 新建一个容器：整个点云的曲率数集
    multi_res = [pool.apply_async(curvature_r_block, args=(xyz,tik[i],tik[i+1], tree, r)) for i in range(cpu)]  # 将每个block需要处理的点云区间发送到每个进程当中
    for res in multi_res:
        curvature_all[tik[j]:tik[j+1]] = res.get()  # 将每个进程得到的结果分block的发送到容器当中
        print('已完成第', tik[j], '至第', tik[j + 1], '的点云')
        j += 1
    pool.close()  # 禁止进程池再接收任务
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算
    return curvature_all  # 返回全部点云曲率集

def Curvature_r_mp_shm(xyz,r=0.04,cpu=mp.cpu_count()):
    '并行按照球半径计算曲率(共享内存)'
    # 准备工作
    pool = mp.Pool(processes=cpu)  # 开启多进程池，数量为cpu
    num = len(xyz)  # 返回点云数量
    # start, end = block(num, cpu)  # 返回每个block的起始点云下标和终止点云下标
    tik = zr.cut_down(num, cpu)  # 去除bug后的分块函数
    tree = KDTree(xyz)  # 创建树
    j = 0  # 分块输出计数器
    curvature_all = np.empty(shape=len(xyz))  # 新建一个容器：整个点云的曲率数集
    '创建共享内存'
    shm = shared_memory.SharedMemory(create=True, size=xyz.nbytes)
    #  将数据复制到共享内存
    shared_array = np.ndarray(xyz.shape, dtype=xyz.dtype, buffer=shm.buf)
    shared_array[:] = xyz[:]
    print(f"共享内存创建完成: {shm.name}")
    print(f"共享内存大小: {shm.size} 字节")
    multi_res = [pool.apply_async(curvature_r_block, args=(shared_array,tik[i],tik[i+1], tree, r)) for i in range(cpu)]  # 将每个block需要处理的点云区间发送到每个进程当中
    for res in multi_res:
        curvature_all[tik[j]:tik[j+1]] = res.get()  # 将每个进程得到的结果分block的发送到容器当中
        print('已完成第', tik[j], '至第', tik[j + 1], '的点云')
        j += 1
    pool.close()  # 禁止进程池再接收任务
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算
    # 清理共享内存
    shm.close()
    shm.unlink()  # 重要：释放共享内存
    return curvature_all  # 返回全部点云曲率集

def curvature_r_block(xyz,start,end,tree,r):
    '分块按照球半径计算曲率'
    # xyz_32 = np.column_stack((xyz[:, 0], xyz[:, 1], xyz[:, 2])).astype(np.float32)
    # pcd = o3d.geometry.PointCloud()
    # pcd.points = o3d.utility.Vector3dVector(xyz_32)
    # pcd_tree = o3d.geometry.KDTreeFlann(pcd)
    curvature_all = np.empty(end-start)
    # num_ = len(xyz_)
    # curvature_all = np.empty(num_)
    j = 0
    for i in tqdm(range(start,end)):
        # [_, idx, _] = pcd_tree.search_knn_vector_3d(pcd.points[i], n)  # 求每个点最近的n个点
        # id_kntree[i, :] = idx  # 求出每个点最邻近的n个点的下标
        xyz_ = xyz[i,:]
        indices, dises = tree.query_radius(xyz_.reshape(1, -1), r=r, return_distance=True,
                                           sort_results=True)  # 返回每个点的邻近点下标列表
        indices = indices[0]
        xyz_n = xyz[indices, :]
        cv, _ = zr.pca(xyz_n)  # 求每个点的特征值和特征向量
        c = zr.curvature_(cv,-1)  # 求出当前点的曲率
        # print(c)
        curvature_all[j] = c
        j += 1
    return curvature_all


def Curvature_r(xyz,r=0.04,job=-1):
    '按照球半径计算曲率'
    num = len(xyz)
    curvature_all = np.empty(num)
    tree = KDTree(xyz)  # 创建树
    for i in tqdm(range(num)):
        xyz_ = xyz[i,:]
        indices, dises = tree.query_radius(xyz_.reshape(1, -1), r=r, return_distance=True,
                                           sort_results=True)  # 返回每个点的邻近点下标列表
        indices = indices[0]
        xyz_n = xyz[indices, :]
        cv, _ = zr.pca(xyz_n)  # 求每个点的特征值和特征向量
        c = zr.curvature_(cv,job)  # 求出当前点的曲率
        # print(c)
        curvature_all[i] = c

    return curvature_all

def get_JCFI_mp(xyzic: Union[list, np.ndarray],ps_out: Union[list, np.ndarray], r: float,cpu:int = mp.cpu_count()) ->np.ndarray:
    '计算JCFI指数'
    '1.求曲率'
    C_all = Curvature_r_mp(xyzic[:, :3], r=0.04,cpu=cpu)
    '2.求平均凸起'
    ps = np.r_[xyzic,ps_out]
    del ps_out
    xzrc = zs.fit_circle(xyzic[:, 0], xyzic[:, 2], xyzic[:, 4], num_cpu=cpu)
    # xzry = zs.fit_circle(xyzic[:, 0], xyzic[:, 2], xyzic[:, 1], num_cpu=cpu)
    # xyziy = np.c_[ps[:, :4], ps[:, 1]]
    # dis_all = zs.get_CenterDis(xzry,xyziy,cpu_count=cpu)
    dis_all = zs.get_CenterDis(xzrc, ps, cpu_count=cpu)
    # tree = KDTree(xyzic)
    # del xzry,xyziy
    tree = KDTree(ps[:, :3])  # 创建树
    del ps
    dis_in = get_nei_dis_mp(xyzic[:, :3], r, tree, dis_all, cpu=cpu)
    '3.求点云左右密度差'
    # 求点云角度
    x0 = np.mean(xzrc[:, 0])
    z0 = np.mean(xzrc[:, 1])
    angle_all = zs.get_angle_all(xyzic[:,[0,2]],x0,z0,cpu_count=cpu)
    ps_Cda = np.c_[xyzic,C_all,dis_in,angle_all]
    ca = np.c_[xyzic[:,4],angle_all]
    dd_all = get_nei_line_density_mp(ca,cpu=cpu)
    ps_Cda = ps_Cda[ps_Cda[:, 4].argsort()]
    xyzicJ = np.c_[ps_Cda[:,:7],dd_all,ps_Cda[:,5]*ps_Cda[:,6]*dd_all]
    # xyzicJ = np.c_[xyzic,ps_Cda[:,5]*ps_Cda[:,6]*dd_all]
    # 将 NaN 替换为 0
    xyzicJ = np.nan_to_num(xyzicJ, nan=0.0)
    return xyzicJ

def get_JCFI_noout(xyzic: Union[list, np.ndarray], r: float, cpu:int = mp.cpu_count(), R=2.7) ->np.ndarray:
    '求JCFI(无非衬砌点情况)'
    '1.求曲率'
    C_all = Curvature_r_mp_shm(xyzic[:, :3], r=r,cpu=cpu)
    '2.求平均凸起'
    xzrc = zs.fit_circle(xyzic[:, 0], xyzic[:, 2], xyzic[:, 4], num_cpu=cpu)
    dis_all = zs.get_CenterDis(xzrc, xyzic, cpu_count=cpu)
    tree = KDTree(xyzic[:, :3])  # 创建树
    dis_in = get_nei_dis_mp(xyzic[:, :3], r, tree, dis_all, cpu=cpu)
    '3.求点云左右密度差'
    x0 = np.mean(xzrc[:, 0])
    z0 = np.mean(xzrc[:, 1])
    angle_all = zs.get_angle_all(xyzic[:,[0,2]],x0,z0,cpu_count=cpu)
    ps_Cda = np.c_[xyzic,C_all,dis_in,angle_all]
    ca = np.c_[xyzic[:,4],angle_all]
    dd_all = get_nei_line_density_mp(ca,cpu=cpu)
    ps_Cda = ps_Cda[ps_Cda[:, 4].argsort()]
    '4.计算周长'
    # perimeter = angle_all / 360 * 2 * np.pi * R  # 基于周长求各点实际位置
    # perimeter = perimeter[ps_Cda[:, 4].argsort()]
    angle_all = zs.get_angle_all(ps_Cda[:, [0, 2]], x0, z0, cpu_count=cpu)
    perimeter = angle_all / 360 * 2 * np.pi * R
    # xyzicJ = np.c_[xyzic, ps_Cda[:, 5] * ps_Cda[:, 6] * dd_all]
    # xyzicJ = np.c_[ps_Cda[:, :7], dd_all, ps_Cda[:, 5] * ps_Cda[:, 6] * dd_all]
    xyzicJP = np.c_[ps_Cda[:,:5], ps_Cda[:, 5] * ps_Cda[:, 6] * dd_all,perimeter]
    # 将 NaN 替换为 0
    xyzicJP = np.nan_to_num(xyzicJP, nan=0.0)
    return xyzicJP

def get_JCFI_ZF(xyzic: Union[list, np.ndarray], r: float,cpu:int = mp.cpu_count(),R=2.7) ->np.ndarray:
    '求JCFI(纵缝版)'
    '1.求曲率'
    C_all = Curvature_r_mp_shm(xyzic[:, :3], r=r,cpu=cpu)
    '2.求平均凸起'
    xzrc = zs.fit_circle(xyzic[:, 0], xyzic[:, 2], xyzic[:, 4], num_cpu=cpu)
    dis_all = zs.get_CenterDis(xzrc, xyzic, cpu_count=cpu)
    tree = KDTree(xyzic[:, :3])  # 创建树
    dis_in = get_nei_dis_mp(xyzic[:, :3], r, tree, dis_all, cpu=cpu)
    '3.求点云左右密度差'
    x0 = np.mean(xzrc[:, 0])
    z0 = np.mean(xzrc[:, 1])
    angle_all = zs.get_angle_all(xyzic[:,[0,2]],x0,z0,cpu_count=cpu)
    ps_Cda = np.c_[xyzic,C_all,dis_in,angle_all]
    ca = np.c_[xyzic[:,4],angle_all]
    dd_all = get_nei_line_density_mp(ca,cpu=cpu)
    ps_Cda = ps_Cda[ps_Cda[:, 4].argsort()]
    # xyzicJ = np.c_[xyzic, ps_Cda[:, 5] * ps_Cda[:, 6] * dd_all]
    # xyzicJ = np.c_[ps_Cda[:, :7], dd_all, ps_Cda[:, 5] * ps_Cda[:, 6] * dd_all]
    '4.计算周长'
    # perimeter = angle_all / 360 * 2 * np.pi * R  # 基于周长求各点实际位置
    # perimeter = perimeter[ps_Cda[:, 4].argsort()]
    angle_all = zs.get_angle_all(ps_Cda[:, [0, 2]], x0, z0, cpu_count=cpu)
    perimeter = angle_all / 360 * 2 * np.pi * R
    xyzicJpC = np.c_[ps_Cda[:,:5], ps_Cda[:, 5] * ps_Cda[:, 6] * dd_all, perimeter,ps_Cda[:, 5]]
    # 将 NaN 替换为 0
    xyzicJpC = np.nan_to_num(xyzicJpC, nan=0.0)
    return xyzicJpC

def get_VY(shared_array,r,tree,i):
    '计算单点的Y方向分量'
    indices= tree.query_radius(shared_array[i,:3].reshape(1, -1), r=r, return_distance=False,
                                       sort_results=False)  # 返回每个点的邻近点下标列表
    indices = indices[0]
    xyz_ = shared_array[indices,:3]
    if len(xyz_)>=3:
        cov = np.cov(xyz_.T)
        eigenvals, eigenvecs = np.linalg.eigh(cov)
        v1 = eigenvecs[:, -1]  # 最大特征值对应的方向（主方向）
        vY = v1[1]
    else:
        vY = 0
    return vY

def get_HF_bulge(c_all,c_interval=500,c_long=20,num_min=40):
    '基于环缝凸起提取'
    # 整理截面序列与点数量
    c_un, num_c = np.unique(c_all, return_counts=True)
    # print(np.mean(num_c))
    # print(np.std(num_c))
    cn = np.c_[c_un,num_c]
    # 找到最大索引
    ind_max = np.argmax(num_c)
    c_max = c_un[ind_max]
    c_max_l = c_max-c_long
    c_max_r = c_max+c_long  # 假定左右缝极限
    # 筛选范围内的数据
    mask = (c_un >= c_max_l) & (c_un <= c_max_r) & (num_c >= num_min)
    # 获取满足条件的c_un值
    c_un_min = np.min(c_un)
    c_un_max = np.max(c_un)
    c_num_long = int(np.ceil((c_un_max-c_un_min)/c_interval))  # 假想环缝数量
    c_lf_all = np.zeros([c_num_long,2])  # 环缝起始和结束位置容器
    # valid_c_un = c_un[mask]  # 极低值起始和结束
    ind_c0_begin = (c_max-c_un_min) % c_interval + c_un_min # 假想起始位置
    for i in range(c_num_long):
        id_min_i_ =  (c_un >= (ind_c0_begin-c_long*7)) & (c_un <= (ind_c0_begin+c_long*7))  # 搜索极低值半径
        cn_ = cn[id_min_i_,:]  # 搜索半径内的数据
        id_max_ = np.argmax(cn_[:,1])  # 点数量最多的位置
        c_name_max = cn_[id_max_,0] # 所在截面序列号
        mask_ = (c_un >= c_name_max-c_long) & (c_un <= c_name_max+c_long) & (num_c >= num_min)  # 复合条件的索引
        valid_c_un_ = c_un[mask_]  # 极低值起始和结束
        c_lf_all[i,0]=valid_c_un_[0]
        c_lf_all[i,1]=valid_c_un_[-1]  # 环缝起始和结束位置
        # 刷新假想位置
        ind_c0_begin += c_interval
    # 创建所有范围的条件
    # 方法1：删除起始值和结束值都为0的行
    mask = ~((c_lf_all[:, 0] == 0) & (c_lf_all[:, 1] == 0))
    c_lf_all = c_lf_all[mask]
    print('环缝截面区间',c_lf_all)
    conditions = [(c_all >= start) & (c_all <= end)
                  for start, end in c_lf_all]
    # 合并所有条件
    final_mask = np.logical_or.reduce(conditions)
    inverse_mask = ~final_mask
    return final_mask, inverse_mask, c_lf_all

def get_HF_bulge_scipy(c_all,c_long=20,num_min=40):
    '基于环缝凸起提取'
    c_un, num_c = np.unique(c_all, return_counts=True)
    peaks, properties = find_peaks(num_c,height=np.mean(num_c) * 0.5,  # 最小峰值高度
                                   distance=int(len(num_c) * 0.1),  # 峰值间最小距离
                                   prominence=np.std(num_c) * 0.3)  # 峰值突出度
    c_un_maxes = c_un[peaks]  # 峰值对应的c值
    num_c_un_maxes = len(c_un_maxes)  # 峰值的数量
    c_lf_all = np.zeros([num_c_un_maxes, 2])  # 环缝起始和结束位置容器
    for i in range(num_c_un_maxes):
        mask_ = (c_un >= c_un_maxes[i]-c_long) & (c_un <= c_un_maxes[i]+c_long) & (num_c >= num_min)  # 复合条件的索引
        valid_c_un_ = c_un[mask_]  # 极低值起始和结束
        c_lf_all[i,0]=valid_c_un_[0]
        c_lf_all[i,1]=valid_c_un_[-1]  # 环缝起始和结束位置
    print('环缝截面区间', c_lf_all)
    conditions = [(c_all >= start) & (c_all <= end)
                  for start, end in c_lf_all]
    # 合并所有条件
    final_mask = np.logical_or.reduce(conditions)
    inverse_mask = ~final_mask
    return final_mask, inverse_mask, c_lf_all

def get_HF_JCFI(ps,r=0.07,cpu=mp.cpu_count()):
    '基于JCFI提取环缝'
    # 1.将大于阈值的点提取出来
    mean_J = np.mean(ps[:,5])  # JCFI均值
    std_J = np.std(ps[:,5])  # JCFI标准差
    v_J = mean_J+std_J*3
    # v_J = 0.079
    print('均值为',mean_J,'标准差为',std_J,'阈值为',v_J)
    # 剔除第一波点云
    ps_J = ps[ps[:, 5] > v_J, :]  # 符合条件的环缝
    ps_no_1 = ps[ps[:,5]<=v_J,:] # 第一轮被剔除的环缝
    # 2.计算ps_J在Y轴方向的分量
    tree = KDTree(ps_J[:, :3])  # 创建树
    num_J = len(ps_J)  # 种子点数量
    vectors_Y = np.zeros(num_J)  # Y方向分量
    '创建共享内存'
    shm = shared_memory.SharedMemory(create=True, size=ps_J.nbytes)
    #  将数据复制到共享内存
    shared_array = np.ndarray(ps_J.shape, dtype=ps_J.dtype, buffer=shm.buf)
    shared_array[:] = ps_J[:]
    print(f"共享内存创建完成: {shm.name}")
    print(f"共享内存大小: {shm.size} 字节")
    '开启并行计算'
    pool = mp.Pool(processes=cpu)
    multi_res = pool.starmap_async(get_VY, ((shared_array,r,tree,i) for i in
                 tqdm(range(num_J),desc='分配任务计算单点Y方向分量',unit='个点',total=num_J)))
    j = 0
    for res in tqdm(multi_res.get(),total=num_J,desc='输出Y方向分量'):
        vectors_Y[j] = res
        j += 1
    pool.close()  # 关闭所有进程
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算
    # 清理共享内存
    shm.close()
    shm.unlink()  # 重要：释放共享内存
    # 3.高斯混合模型分解成三类，要接近0那类
    labels = zm.use_gmm(vectors_Y.reshape(-1, 1),3)
    gmm_0 = vectors_Y[labels == 0]
    gmm_1 = vectors_Y[labels == 1]
    gmm_2 = vectors_Y[labels == 2]
    # 计算每个类别的平均值
    mean_0 = np.mean(gmm_0)
    mean_1 = np.mean(gmm_1)
    mean_2 = np.mean(gmm_2)
    # 计算与0的距离（绝对值）
    dist_0 = abs(mean_0)
    dist_1 = abs(mean_1)
    dist_2 = abs(mean_2)
    # 找到距离0最近的类别
    distances = [dist_0, dist_1, dist_2]
    min_index = distances.index(min(distances))
    # 根据索引选择对应的数组
    if min_index == 0:
        ps_gmm = ps_J[labels == 0, :]
        ps_no_2 = ps_J[labels == 1, :]
        ps_no_3 = ps_J[labels == 2, :]
    elif min_index == 1:
        ps_gmm = ps_J[labels == 1, :]
        ps_no_2 = ps_J[labels == 0, :]
        ps_no_3 = ps_J[labels == 2, :]
    else:
        ps_gmm = ps_J[labels == 2, :]  # 为下一步准备的点云
        ps_no_2 = ps_J[labels == 0, :]
        ps_no_3 = ps_J[labels == 1, :]  # 剔除的点云
    # 4. 实例分割并返回环缝截面序列
    in_index,out_index,hf_lf = get_HF_bulge(ps_gmm[:,4])
    # 5.输出环缝点云，非环缝点云，和环缝点云截面区间集合
    ps_hf = ps_gmm[in_index,:]
    ps_no_4 = ps_gmm[out_index,:]
    ps_no = np.r_[ps_no_1,ps_no_2,ps_no_3,ps_no_4]
    return ps_hf,ps_no,hf_lf

def cut_DGH(xyzic,hf_lf):
    '分割盾构环'
    num_DGH = len(hf_lf)
    list_DGH = []
    for i in range(num_DGH):
        xyzic_l = xyzic[xyzic[:,4]<hf_lf[i,0],:]
        list_DGH.append(xyzic_l)
        xyzic=xyzic[xyzic[:,4]>=hf_lf[i,1],:]
    list_DGH.append(xyzic)
    return list_DGH

# def fit_line_by2ps(oy):
#     '两个最远点计算直线kb'
#     ind_y_max = np.argmax(oy[:,1])
#     ind_y_min = np.argmin(oy[:,1])
#     oy_max = oy[ind_y_max,:]
#     oy_min = oy[ind_y_min,:]
#     k = (oy_max[1]-oy_min[1])/(oy_max[0]-oy_min[0])
#     print(k)

def Merge_straight_lines(lines, threshold = 10):
    '合并相同直线'
    distances = squareform(pdist(lines))  # 距离矩阵
    groups = []
    visited = set()
    for i in range(len(lines)):
        if i in visited:
            continue
        group = [i]
        visited.add(i)
        for j in range(i + 1, len(lines)):
            if j not in visited and distances[i, j] < threshold:
                group.append(j)
                visited.add(j)
        groups.append(group)
    print("按距离分组结果：")
    for idx, group in enumerate(groups):
        print(f"组 {idx}: {group}")
    return groups

def get_ZF_JCFI(xyzic,cpu=mp.cpu_count(),r=0.03,eps=0.02,min_samples=4,sigma=0.01):
    '基于JCFI提取每个盾构环的纵缝'
    #1. 计算JCFI均值与标准差
    xyzicjp = get_JCFI_noout(xyzic, r,cpu)
    mean_JCFI = np.mean(xyzicjp[:,5])
    std_JCFI = np.std(xyzicjp[:,5])
    td0 = mean_JCFI+3*std_JCFI  # 严格阈值
    print('严格JCFI阈值',td0)
    #3. 通过DBSCAN聚类并剔除非种子点
    xyzicj_td0 = xyzicjp[xyzicjp[:,5]>=td0,:]
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(xyzicj_td0[:,:3])
    labels = clustering.labels_  # 每个点的类别标签，-1 表示噪声
    xyzicjzl = np.c_[xyzicj_td0,labels]
    xyzicjzl = xyzicjzl[xyzicjzl[:,-1]>=0,:]
    l_un,num_l = np.unique(xyzicjzl[:,-1],return_counts=True)
    seed_index = []  #  种子索引
    C_len = len(np.unique(xyzicjzl[:, 4]))
    for i in l_un:
        xyzicjzl_ = xyzicjzl[xyzicjzl[:,-1]==i,:]
        num_c_ = len(np.unique(xyzicjzl_[:,4]))
        if num_c_>=0.25*C_len:
            seed_index.append(i)
    print('候选种子点索引',seed_index)
    seed_index_in = np.isin(xyzicjzl[:, -1], seed_index)
    xyzicjzl_in = xyzicjzl[seed_index_in, :]
    # zt.view_pointclouds(xyzicjzl_in[:, :3], xyzicjzl_in[:, -1], colormap='hsv')
    print('候选种子点数量',xyzicjzl_in.shape)
    num_seed_index = len(seed_index)
    #4. 对各个联通区域拟合直线pY
    kb_all = np.empty([num_seed_index, 2])  # 直线属性容器
    j = 0
    for i in seed_index:
        xyzicjzl_in_ = xyzicjzl_in[xyzicjzl_in[:,-1]==i,:]
        oy_ = xyzicjzl_in_[:,[6,1]]
        # 二维直线拟合
        kb_all[j,:] = zR.fit_2Dline_ransac(oy_,sigma=sigma)
        j+=1
    #5. 合并相同直线
    groups_lines = Merge_straight_lines(kb_all, 2)
    #6. 重新整理种子点数据
    kb_list = np.empty([len(groups_lines), 2])
    for idx, group in enumerate(groups_lines):
        if len(group)>=2:
            selected_labels = np.array(seed_index)[group]
            xyzicjzl_in_ = xyzicjzl_in[np.isin(xyzicjzl_in[:,-1],selected_labels),:]
            oy_ = xyzicjzl_in[:, [6, 1]]
            kb_list[idx,:] = zR.fit_2Dline_ransac(oy_,sigma=sigma)
        else:
            kb_list[idx, :] = kb_all[idx, :]
    print('联通区域拟合直线属性',kb_list)
    # #7. 找到直线区域平均距离大于0的点数量
    # # 点到直线的距离
    # zf_list =[]
    # td1 = mean_JCFI+1*std_JCFI  # 不严格阈值
    # oy_all = xyzicjz[:,[6,1]]
    # td2 = 0.1  # 距离阈值
    # for i in range(len(kb_list)):
    #     dis_all_ = zm.get_distance_point2line(oy_all,kb_list[i])
    #     ps_ = xyzicjz[dis_all_<td2,:]
    #     ps_ = ps_[ps_[:,5]>td1,:]
    #     num_C_ = len(np.unique(ps_[:,4]))  # 截面数量
    #     if num_C_/C_len >0.5:
    #         zf_list.append(ps_)
    # zf_array = np.vstack(zf_list)
    # 找到符合条件的下标并合并
    zf_bool = np.zeros(len(xyzicjp), dtype=bool)
    td1 = mean_JCFI + 1 * std_JCFI  # 不严格阈值
    td_dis = 0.1  # 距离阈值
    print('不严格JCFI阈值',td1)
    py_all = xyzicjp[:,[6,1]]
    JCFI_all = xyzicjp[:,5]
    for i in range(len(kb_list)):
        dis_all_ = zm.get_distance_point2line(py_all, kb_list[i])
        # 限制条件1
        valid_indices = dis_all_ < td_dis
        # 限制条件2
        condition_mask = JCFI_all > td1
        # 同时满足两个条件的位置
        final_mask = valid_indices & condition_mask
        ps_ = xyzicjp[final_mask,:]
        num_C_ = len(np.unique(ps_[:, 4]))  # 截面数量
        if num_C_ / C_len > 0.5:
            # 将满足条件的位置在zf_bool中设为True
            zf_bool = zf_bool | final_mask  # 使用或操作，累积所有满足条件的位置
    # 返回zf_bool为True的点云
    xyzic_true = xyzicjp[zf_bool, :]
    # 返回zf_bool为False的点云
    xyzic_false = xyzicjp[~zf_bool, :]
    return xyzic_true, xyzic_false

def get_ZF_C(xyzic,cpu=mp.cpu_count(),r=0.035,eps=0.02,min_samples=4,sigma=0.01,R=2.7,td_dis=0.1):
    '基于球曲率求单个盾构环的纵缝'
    '1.计算JCFI和周长'
    xyzicJpC = get_JCFI_ZF(xyzic,r=r,cpu=cpu,R=R)
    # 计算JCFI的严格阈值
    mean_JCFI = np.mean(xyzicJpC[:,5])
    std_JCFI = np.std(xyzicJpC[:,5])
    td0 = mean_JCFI+3*std_JCFI  # 严格阈值
    print('严格JCFI阈值',td0)
    # 寻找第一批候选点
    # xyzicp = np.c_[xyzic,perimeter]
    ps_td0 = xyzicJpC[xyzicJpC[:,5] >= td0, :]
    '2.DBSCAN聚类'
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(ps_td0[:,:3])
    labels = clustering.labels_  # 每个点的类别标签，-1 表示噪
    ps_l = np.c_[ps_td0,labels]
    ps_l = ps_l[ps_l[:, -1] >= 0, :]
    l_un,num_l = np.unique(ps_l[:,-1],return_counts=True)
    seed_index = []  #  种子索引
    C_len = len(np.unique(xyzic[:, 4]))  # 盾构环截面数量
    for i in l_un:
        ps_l_ = ps_l[ps_l[:,-1]==i,:]
        num_c_ = len(np.unique(ps_l_[:,4]))
        if num_c_>=0.25*C_len:
            seed_index.append(i)
    print('候选种子联通索引',seed_index)
    seed_index_in = np.isin(ps_l[:, -1], seed_index)
    ps_in = ps_l[seed_index_in, :]
    print('候选种子点数量', ps_in.shape)
    num_seed_index = len(seed_index)  # 联通区域数量
    '3.对各个联通区域拟合直线pY，合并相近直线'
    # 拟合直线
    kb_all = np.empty([num_seed_index, 2])  # 直线属性容器
    j = 0
    for i in seed_index:
        ps_in_ = ps_in[ps_in[:,-1]==i,:]
        py_ = ps_in_[:,[6,1]]
        # 二维直线拟合
        kb_all[j,:] = zR.fit_2Dline_ransac(py_,sigma=sigma)
        j+=1
    print(kb_all)
    # 合并相同直线
    groups_lines = Merge_straight_lines(kb_all, 2)
    '4.整理最后的种子点数据'
    # 重新整理种子点数据
    kb_list = np.empty([len(groups_lines), 2])
    for idx, group in enumerate(groups_lines):
        if len(group)>=2:
            selected_labels = np.array(seed_index)[group]
            ps_in_ = ps_in[np.isin(ps_in[:,-1],selected_labels),:]
            py_ = ps_in_[:, [6, 1]]
            kb_list[idx,:] = zR.fit_2Dline_ransac(py_,sigma=sigma)
        else:
            kb_list[idx, :] = kb_all[idx, :]
    print('联通区域拟合直线属性',kb_list)
    '5.输出纵缝点和衬砌点'
    # 找到符合条件的下标并合并
    zf_bool = np.zeros(len(xyzic), dtype=bool)
    mean_C = np.mean(xyzicJpC[:,7])
    std_C = np.std(xyzicJpC[:,7])
    td1 = mean_C+3*std_C  # 不严格阈值
    print('严格球曲率阈值',td1)
    py_all = xyzicJpC[:,[6,1]]
    C_all = xyzicJpC[:,7]
    for i in range(len(kb_list)):
        dis_all_ = zm.get_distance_point2line(py_all, kb_list[i])
        # 限制条件1
        valid_indices = dis_all_ < td_dis
        # 限制条件2
        condition_mask = C_all > td1
        # 同时满足两个条件的位置
        final_mask = valid_indices & condition_mask
        ps_ = xyzicJpC[final_mask,:]
        num_C_ = len(np.unique(ps_[:, 4]))  # 截面数量
        if num_C_ / C_len > 0.5:
            # 将满足条件的位置在zf_bool中设为True
            zf_bool = zf_bool | final_mask  # 使用或操作，累积所有满足条件的位置
        # np.savetxt('E:\\2025博二上学期\\基于复合指数的RMLS盾构隧道环缝和纵缝提取\\Data\\test_ps_.txt',ps_,fmt='%.05f')
    # 返回zf_bool为True的点云
    xyzic_true = xyzicJpC[zf_bool, :]
    # 返回zf_bool为False的点云
    xyzic_false = xyzicJpC[~zf_bool, :]
    # np.savetxt('E:\\2025博二上学期\\基于复合指数的RMLS盾构隧道环缝和纵缝提取\\Data\\xyzic_true.txt',xyzic_true,fmt='%.05f')
    # np.savetxt('E:\\2025博二上学期\\基于复合指数的RMLS盾构隧道环缝和纵缝提取\\Data\\xyzic_false.txt',xyzic_false,fmt='%.05f')
    return xyzic_true, xyzic_false

def get_HF_intensity_peaks(ps,length_05 = 15,dis=200):
    '251103强化版本强度值环缝提取算法'
    c_un = np.unique(ps[:,4])
    num_C = len(c_un)
    # 计算每个环的平均强度值
    i_c = np.empty(num_C)
    # 并行计算准备
    tik = zs.cut_down(num_C)  # 分块起止点
    pool = mp.Pool(processes=mp.cpu_count())  # 开启多进程池，数量为cpu
    multi_res = [pool.apply_async(zs.find_cImean_block, args=(ps, c_un, tik[i], tik[i + 1])) for i in  # points_new
                 range(mp.cpu_count())]  # 将每个block需要处理的点云区间发送到每个进程当中
    tik_ = 0  # 计数器
    for res in multi_res:
        i_c[tik[tik_]:tik[tik_ + 1]] = res.get()
        tik_ += 1
    pool.close()  # 禁止进程池再接收任务
    pool.join()  # 当所有进程全部计算完毕后，退出并行计算
    '归一化特征值'
    i_c = zm.normalization(i_c,1.0)
    # 取反
    i_c_1 = 1-i_c
    '计算极低值'
    peaks, properties = find_peaks(i_c_1,height=np.mean(i_c_1)*0.5,  # 最小峰值高度
                                   distance=dis,  # 峰值间最小距离
                                   prominence=np.std(i_c_1) * 0.3)  # 峰值突出度
    c_un_maxes = c_un[peaks]  # 峰值对应的c值
    print('环缝中心截面位置',c_un_maxes)
    num_hf = len(c_un_maxes)  # 环缝数量
    # length_05 = 15  # 假定环缝半宽度
    td = 3
    hf_lf = np.empty([num_hf,2])
    for i in range(num_hf):
        # 找到左右假定搜索边界
        peaks_l_ = peaks[i]-length_05
        peaks_r_ = peaks[i]+length_05
        # 找到左右非环缝边界
        cq_l_ = peaks_l_-length_05
        cq_r_ = peaks_r_+length_05
        # --- 新增：边界检查与修正 ---
        peaks_l_ = max(0, peaks_l_)
        peaks_r_ = min(num_C-1, peaks_r_)  # 索引最大为 num_C - 1
        cq_l_ = max(0, cq_l_)
        cq_r_ = min(num_C-1, cq_r_)  # 索引最大为 num_C - 1
        # --- 结束新增 ---
        # 求左右衬砌的平均标准差和阈值
        i_c_l = i_c[cq_l_:peaks_l_]
        i_c_r = i_c[peaks_r_:cq_r_]
        mean_i_c_l = np.mean(i_c_l)
        std_i_c_l = np.std(i_c_l)
        mean_i_c_r = np.mean(i_c_r)
        std_i_c_r = np.std(i_c_r)
        td_l_ = mean_i_c_l - std_i_c_l * td
        td_r_ = mean_i_c_r - std_i_c_r * td
        # 左右待选值
        i_c_hf_l = i_c[peaks_l_:peaks[i]]
        i_c_hf_r = i_c[peaks[i]:peaks_r_]
        # 在 i_c_l 中查找最后一个小于 td_l_ 的元素的相对下标
        indices_l = np.where(i_c_hf_l < td_l_)[0]
        if len(indices_l) > 0:
            last_idx_l_rel = indices_l[0]
        else:
            last_idx_l_rel = 0
        indices_r = np.where(i_c_hf_r < td_r_)[0]
        if len(indices_r) > 0:
            first_idx_r_rel = indices_r[-1]
        else:
            first_idx_r_rel = 14
        # 整理左右下标
        idx_l_ = peaks[i] - length_05 + last_idx_l_rel
        idx_r_ = peaks[i] + first_idx_r_rel
        idx_r_ = min(idx_r_, num_C-1)
        hf_lf[i,0] = c_un[idx_l_]
        hf_lf[i,1] = c_un[idx_r_]
    print('环缝截面起止位置',hf_lf)
    # 确保 hf_lf 是整数类型，因为它们将用作索引
    hf_lf = hf_lf.astype(int)
    # 假设 ps[:, 4] 存储的是环的索引 c
    c_indices = ps[:, 4]
    # 创建一个布尔掩码，标记哪些点属于环缝
    mask_hf = np.zeros(len(ps), dtype=bool)
    for start, end in hf_lf:
        # 创建当前环缝范围的掩码，并与总掩码进行或运算
        mask_hf |= (c_indices >= start) & (c_indices <= end)
    # 使用掩码分割数据
    ps_hf = ps[mask_hf]  # 环缝部分
    ps_nf = ps[~mask_hf]  # 非环缝部分 (~ 是逻辑非运算符)
    return ps_hf, ps_nf


"""构建四棱锥 Mesh 网格表示的示例。

使用自定义的 MeshData 数据结构，通过参数化方法指定锥底及锥顶坐标，
在控制台打印网格的顶点与面片索引，展示顶点-面片索引机制。
"""

from src import create_pyramid_mesh


def main() -> None:
    # 创建一个底面 2000x2000mm，高 2000mm 的四棱锥网格
    pyramid = create_pyramid_mesh(2000.0, 2000.0, 2000.0)

    print("=" * 60)
    print(f" 成功建立 Mesh 几何网格：{pyramid.name} ")
    print("=" * 60)

    # 1. 打印顶点
    print(f"[网格顶点 (Vertices)] 共 {len(pyramid.vertices)} 个:")
    for idx, v in enumerate(pyramid.vertices):
        print(f"  MV{idx}: ({v.x:.1f}, {v.y:.1f}, {v.z:.1f})")

    # 2. 打印面片 (三角面与底面四边形面)
    print(f"\n[多边形面片 (Faces)] 共 {len(pyramid.faces)} 个面片:")
    for idx, face in enumerate(pyramid.faces):
        shape_type = "四边形" if len(face) == 4 else "三角形"
        print(f"  MF{idx} ({shape_type}): 包含顶点索引 {face}")

    print("=" * 60)


if __name__ == "__main__":
    main()

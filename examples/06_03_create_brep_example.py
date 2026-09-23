"""构建长方体 B-Rep 边界表示的示例。

手动建立长方体的 8 个顶点、12 条棱边和 6 个表面的拓扑连接关系，
并打印该拓扑结构的所有构成元素。
"""

from src import create_cube_brep


def main() -> None:
    # 创建一个 2000mm x 2000mm x 2000mm 的正方体
    cube = create_cube_brep(2000.0, 2000.0, 2000.0)

    print("=" * 60)
    print(f" 成功建立 B-Rep 几何体：{cube.name} ")
    print("=" * 60)

    # 1. 打印顶点
    print(f"[顶点 (Vertices)] 共 {len(cube.vertices)} 个:")
    for idx, v in enumerate(cube.vertices):
        print(f"  V{idx}: ({v.x:.1f}, {v.y:.1f}, {v.z:.1f})")

    # 2. 打印边
    print(f"\n[棱边 (Edges)] 共 {len(cube.edges)} 条:")
    for idx, edge in enumerate(cube.edges):
        print(f"  E{idx}: 顶点 V{edge[0]} ---> 顶点 V{edge[1]}")

    # 3. 打印面
    print(f"\n[表面 (Faces)] 共 {len(cube.faces)} 个面:")
    for idx, face in enumerate(cube.faces):
        print(f"  F{idx}: 闭合顶点环 {face}")

    print("=" * 60)


if __name__ == "__main__":
    main()

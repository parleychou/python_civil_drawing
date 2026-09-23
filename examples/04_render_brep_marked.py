"""以不同颜色和标签分类渲染 B-Rep 各拓扑要素。

分别提取顶点、边、面进行差异化着色，并利用 RenderEngine 为顶点添加文本标签，
以帮助学生直观理解三维边界表示法的数据要素。
"""

import sys
from pathlib import Path
_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


import sys
from pathlib import Path

# 动态寻找第 04 章的脚本目录，以便导入公共的 RenderEngine
def find_chapter_scripts(prefix: str) -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        try:
            for child in parent.iterdir():
                if child.is_dir() and child.name.startswith(prefix):
                    for sub_name in ("src", "scripts"):
                        sub = child / sub_name
                        if sub.exists():
                            return sub
                    return child
        except OSError:
            continue
    return Path()

scripts_dir = Path(__file__).resolve().parent
ch4_path = find_chapter_scripts("04")
sys.path.insert(0, str(scripts_dir))
if ch4_path.exists():
    sys.path.insert(0, str(ch4_path))

from brep_primitives import create_cube_brep
from render_engine import RenderEngine


def main() -> None:
    # 1. 实例化长方体 B-Rep 对象
    cube = create_cube_brep(2000.0, 2000.0, 2000.0)

    # 2. 初始化课件渲染引擎
    engine = RenderEngine(window_size=(1024, 768), show_grid=True)

    # 3. 渲染表面 (Faces) —— 浅蓝色半透明
    engine.add_mesh(
        cube.to_pyvista(),
        color="lightblue",
        show_edges=False,
        opacity=0.4
    )

    # 4. 渲染边 (Edges) —— 钢青色线段
    engine.add_mesh(
        cube.get_edges_polydata(),
        color="steelblue",
        show_edges=True
    )

    # 5. 渲染顶点并贴上标签 (Vertices) —— 珊瑚红点与 V0-V7 标签
    for idx, v in enumerate(cube.vertices):
        engine.render_point(
            v.to_tuple(),
            color="coral",
            point_size=15.0,
            label=f"V{idx}"
        )

    # 6. 显示窗口并提示控制指令
    print(f"[*] 正在渲染 B-Rep 立方体...")
    print(f"    - 表面：淡蓝色半透明 (lightblue)")
    print(f"    - 棱边：钢青色细线 (steelblue)")
    print(f"    - 顶点：珊瑚红色圆点 (coral) + 顶点标签")
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()

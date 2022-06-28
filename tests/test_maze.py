from sgtpyutils.maze import *

g_map = '01020202000200020000020000020002000202000200020200020202000202020202000202020002020202000202020200020000020000020000020000000200000202000002000002000202020002000002000202020202020002020002020200020000020202020202000000020202000202020002000002020002020002000002020200020002000202020000020000020000000200000200000002000200000200020200000000000200020202020202000202020002020202000202020202000202000202020200020002000000020000000200000200000202020000020200020002020002000202020200020002020202020200020202000002000002020002020200000202000200000002020200020002000002000202000202020002020002000202000202020002020200020002020000020000000200000002000002000200000202020000020200020200020000020202020202000002000200020202020002000002000202000202000002020000000200000202020200020000020000000202020202020000020000020002020202020202000000020202020002000202020002000002000002000202000002000002000200020002000002020202020002000200020202000202000202020200020002020002020200020200020000000002000202000202000200000002000202020002000000000202000002000202020202020000000200020202020202020000020202000202000200020202000200000002020200020000020000020000000200020000000202020202000000020202000200020002020002020202020202020202020200020002000000020202000200000202000002020200020000000002000200020202020200020202000200000200020002000200000002020202000202000000020002000200020000000202020202000202000202020200020002020002000200000200020002020202020000020000020002020000020200000200020202020202020202020200000200000202020202000002000200020202000200020002000200020000000202020202020002000002020200020002000002020000020200020002020202020002000002000200020200020002000202000002000200000002000200000002020002000202000200020200020200000202020200020202020200020202000200000202000002020002000000020002020002000200000002000200020202020202020002000200020202020202020200000200020002020002020002000002000200020202020200000200020000020202020202020200020002020202020200020202000200020202020002000200020000020002000202020200020002000000020000020000000000000202020002020202000202020000020203FFFFFFFF'
g_map = bytes.fromhex(g_map)


def test_single_resolve():
    maze = Maze(
        map_data=g_map,
        map_sizex=32,
        start=Pos(0, 0),
        end=b'\x03',
        directions=None,
        avoid=[b'\x00'],
        allow=None
    )
    data = maze.explore()
    result = maze.dump()
    assert result == ['dddsddssddddsdsssddwwdddddwwddwdddddsssddsddssddssssaawaaawaaassaaassassaaaawwawwwdwwaasasasssasasaaaasssaasassddddwdddssasaaaaassssddssddwddddsdddwwawwwwddwwwdddwwwdddddddddsdddsssdssssdsssaassdd']


def test_multi_resolve():
    maze = Maze(
        map_data=g_map,
        map_sizex=32,
        start=Pos(0, 0),
        end=b'\x03',
        directions=None,
        avoid=[b'\x00'],
        allow=None,
        max_result_count=10
    )
    data = maze.explore()
    result = maze.dump()
    assert len(result) == 10


def test_custom_item():
    maze = Maze(
        map_data='*11110100001010000101111#',
        map_sizex=5,
        start=Pos(0, 0),
        end='#',
        directions=None,
        avoid=['1'],
        allow=None,
        max_result_count=10
    )
    maze.print_map(convert={'0':' '})
    data = maze.explore()
    result = maze.dump()
    assert result == ['sssddwwddsss']

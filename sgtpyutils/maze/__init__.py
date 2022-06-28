from __future__ import annotations
import string
from typing import Dict, List, Tuple, overload
from ..logger import logger


class Pos(Tuple):
    @overload
    def __new__(self, pos: Pos) -> Pos:
        ...

    @overload
    def __new__(self, x: int = 0, y: int = 0) -> Pos:
        ...

    def __new__(self, x: any = None, y: int = None) -> Pos:
        if x is None:
            x = 0
            y = 0
        if isinstance(x, Pos):
            x = x.x
            y = x.y
        return super().__new__(self, [x, y])

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @x.setter
    def x(self, val):
        self[0] = val

    @y.setter
    def y(self, val: int):
        self[1] = val

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Pos):
            return self.x == __o.x and self.y == __o.y
        return False

    def equal(self, x: int, y: int) -> bool:
        # speed up
        return self.x == x and self.y == y

    def move(self, x: int = 0, y: int = 0):
        self.x += x
        self.y += y

    def __repr__(self) -> str:
        return f'Pos[{self.x},{self.y}]'


class Maze:
    default_directions = {
        'a': [-1, 0],
        'd': [1, 0],
        'w': [0, -1],
        's': [0, 1],
    }

    def get_index_by_pos(self, pos: Pos) -> int:
        return pos.x + pos.y * self.map_sizex

    def get_pos_by_index(self, index: int) -> Pos:
        x = index % self.map_sizex
        y = index // self.map_sizex
        return Pos(x, y)

    def __init__(self, map_data: List, map_sizex: int, start: Pos | any, end: Pos | any, avoid: List[any] = None, allow: List[any] = None, directions: Dict = default_directions, max_result_count: int = 1):
        '''
        map_data:       List draw a map
        map_sizex:      int pos-x of the map , to determine map's shape
        start:Pos:      player start position or start-pos-data , if set data , then will find in map_data and convert to pos
        end:Pos         player end position or end-pos-data , if set pos , then will convert pos to a data and modify map_data
        avoid:List[any] when moving position's data in this , player will die. `avoid` and `allow` should only set one of them
        allow:List[any] when moving position's data in this , nothing happend. `avoid` and `allow` should only set one of them
        directions:Dict determine which direction is allowed to move , default is `up` `down` `left` `right`
        max_result_count:int if get enough result , then directly ret
        '''
        self.data = map_data
        self.map_sizex = map_sizex
        self.map_sizey = len(self.data) // self.map_sizex
        map_data_dict = {}
        for index, key in enumerate(map_data):
            if key in map_data_dict:
                continue
            map_data_dict[key] = index
        if isinstance(start, Pos):
            self.start = start
        else:
            assert start in map_data_dict, f'start data [{start}] not found in map_data'
            index = map_data_dict[start]
            self.start = self.get_pos_by_index(index)
            logger.info(f'self start-pos\'s pos is set to {self.start}')

        if isinstance(end, Pos):
            for i in string.printable:
                if not i in map_data:
                    self.end = i
                    index = self.get_index_by_pos(end)
                    map_data[index] = i
                    logger.info(f'end-pos\'s data is set to char {i} at {end}')
                    break
        else:
            self.end = end
        self.directions = directions or Maze.default_directions
        assert not (
            avoid and allow), '`avoid` and `allow` should set one of them'
        assert avoid or allow, '`avoid` and `allow` should set one of them'
        if avoid:
            avoid_dict = {}
            for i in avoid:
                avoid_dict[i] = True
            self.avoid = avoid_dict
        else:
            for i in allow:
                if i in map_data_dict:
                    del map_data_dict
            self.avoid = map_data_dict
        self.max_result_count = max_result_count
        self.init_solution()
        pass

    def init_solution(self):
        self.visited: Dict[str, bool] = {}
        self.paths: List[str] = []
        self.result_count = 0
        self.dump_result = None

    def dump_map(self, convert: Dict[any, any] = {}):
        result = []
        r = []
        for index, i in enumerate(self.data):
            if not (index % self.map_sizex):
                result.append(r)
                r = []
            data = self.data[index:index+1]
            if data in convert:
                data = convert[data]
            r.append(data)
        result.append(r)
        return result

    def print_map(self, convert: Dict[any, any] = {}):
        data = [''.join([''.join([str(c) for c in y]) for y in x])
                for x in self.dump_map(convert)]
        print('\n'.join(data))

    def dump(self):
        if self.dump_result:
            return self.dump_result
        if not self.result:
            self.result = self.explore()
        assert self.result, 'fail to solve'
        self.dump_result = []
        self.__dump(self.result, [])
        return self.dump_result

    def __dump(self, dic: Dict, r: List):
        if dic == None or dic == True:
            self.dump_result.append(''.join(r))
            return
        for k in dic:
            r.append(k)
            self.__dump(dic[k], r)
            r.pop()

    def explore(self):
        self.init_solution()
        x, y = self.start
        self.result = self.__explore(x, y)
        return self.result

    def __explore(self, x: int, y: int):
        k = f'{x}:{y}'
        if x < 0 or y < 0 or x >= self.map_sizex or y >= self.map_sizey:
            return None
        if k in self.visited:
            return None
        p = self.map_sizex*y+x
        v = self.data[p:p+1]
        if v in self.avoid:
            return None
        if v == self.end:
            self.result_count += 1
            return True
        result = {}
        self.visited[k] = True
        for d in self.directions:
            # paths.append('a')
            dx, dy = self.directions[d]
            r = self.__explore(x+dx, y+dy)
            if r:
                result[d] = r
            # paths.pop()
            if self.result_count >= self.max_result_count:
                break

        del self.visited[k]
        return result

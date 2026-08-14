/**
 * 系统管理相关
 */
// import { requestReturn } from "@/util/typeAndEnum";
import { AxiosPromise, AxiosResponse } from "axios";
import service from "./request"

// 查询角色列表
export function listRole(query: any) {
  return service({
    url: "/system/role/list",
    method: "get",
    params: query,
  });
}

// 查询角色详细
export function getRole(roleId: number) {
  return service({
    url: "/system/role/" + roleId,
    method: "get",
  });
}

// 新增角色
export function addRole(data: any) {
  return service({
    url: "/system/role",
    method: "post",
    data: data,
  });
}

// 修改角色
export function updateRole(data: any) {
  return service({
    url: "/system/role",
    method: "put",
    data: data,
  });
}

// 角色数据权限
export function dataScope(data: any) {
  return service({
    url: "/system/role/dataScope",
    method: "put",
    data: data,
  });
}

// 角色状态修改
export function changeRoleStatus(roleId: number, status: string) {
  const data = {
    roleId,
    status,
  };
  return service({
    url: "/system/role/changeStatus",
    method: "put",
    data: data,
  });
}

// 删除角色
export function delRole(roleId: number) {
  return service({
    url: "/system/role/" + roleId,
    method: "delete",
  });
}

// 真tm邪门，这接口若依居然是从里面拿角色选项的
export function getRoleOption() {
  return service({
      url: "/system/user/",
      method: "get",
  });
}


// 查询部门下拉树结构
export function deptTreeselect(params?: any) {
  return service({
    url: "/system/dept/treeselect",
    method: "get",
    params,
  });
}

// 查询菜单列表
export function listMenu(menuName: string | null = null, visible: number | null = null) {
  return service({
    url: "/system/menu/list",
    method: "get",
    params: {
      menuName,
      visible,
    },
  });
}

// 根据角色ID查询菜单下拉树结构
export function roleMenuTreeselect(roleId: number) {
  return service({
    url: "/system/menu/roleMenuTreeselect/" + roleId,
    method: "get",
  });
}

// 新增菜单
export function addMenu(data: any) {
  return service({
    url: "/system/menu",
    method: "post",
    data: data,
  });
}

// 修改菜单
export function updateMenu(data: any) {
  return service({
    url: "/system/menu",
    method: "put",
    data: data,
  });
}

// 删除菜单
export function delMenu(menuId: number) {
  return service({
    url: "/system/menu/" + menuId,
    method: "delete",
  });
}


// 查询部门列表
export function listDept(query: any) {
  return service({
    url: '/system/dept/list',
    method: 'get',
    params: query
  });
}
// 删除部门
export function delDept(deptId: number) {
  return service({
    url: '/system/dept/' + deptId,
    method: 'delete'
  })
}

// 新增部门
export function addDept(data: any) {
  return service({
    url: '/system/dept',
    method: 'post',
    data: data
  });
}

// 修改部门
export function updateDept(data: any) {
  return service({
    url: '/system/dept',
    method: 'put',
    data: data
  });
}

// 查询部门详细
export function getDept(deptId: number) {
  return service({
    url: '/system/dept/' + deptId,
    method: 'get'
  })
}

// 查询部门列表（排除节点）
export function listDeptExcludeChild(deptId: number) {
  return service({
    url: '/system/dept/list/exclude/' + deptId,
    method: 'get'
  })
}

// 获取我的菜单路由
export const getRouters = () => {
  return service({
    url: "/getRouters",
    method: "get",
  });
};

// 清理参数缓存
export function clearCache() {
  return service({
    url: "/system/dict/type/clearCache",
    method: "delete",
  });
}

// 删除字典类型
export function delDict(dictId: number) {
  return service({
    url: "/system/dict/type/" + dictId,
    method: "delete",
  });
}
// 查询字典类型列表
export function listDict(query:any) {
  return service({
    url: "/system/dict/type/list",
    method: "get",
    params: query,
  });
}
// 查询字典类型详细
export function getDict(dictId:number) {
  return service({
    url: "/system/dict/type/" + dictId,
    method: "get",
  });
}
// 修改字典类型
export function updateDict(data:any) {
  return service({
    url: "/system/dict/type",
    method: "put",
    data: data,
  });
}
// 新增字典类型
export function addDict(data:any) {
  return service({
    url: "/system/dict/type",
    method: "post",
    data: data,
  });
}
// 查询字典数据列表
export function listDetailDict(query:any) {
  return service({
    url: "/system/dict/data/list",
    method: "get",
    params: query,
  });
}
// 查询字典数据详细
export function getDictDetail(dictCode:any) {
  return service({
    url: "/system/dict/data/" + dictCode,
    method: "get",
  });
}
// 删除字典数据
export function delDictDetail(dictCode:any) {
  return service({
    url: "/system/dict/data/" + dictCode,
    method: "delete",
  });
}
// 新增字典数据
export function addDictDetail(data:any) {
  return service({
    url: "/system/dict/data",
    method: "post",
    data: data,
  });
}
// 修改字典数据
export function updateDictDetail(data:any) {
  return service({
    url: "/system/dict/data",
    method: "put",
    data: data,
  });
}

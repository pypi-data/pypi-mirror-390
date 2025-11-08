# pymod112

一个基于Python开发的公民身份号码检验与地区代码查找程序

by HoshsL

## 安装

[PyPI](https://pypi.org/project/pymod112/) 

使用pip安装，仅支持Python 3.10及以上版本

```sh
pip install pymod112
```

## 使用

校验身份证号码(隐藏详情)

```python
>>> import pymod112
>>> pymod112.mod112('11010519491231002X')
True
```

校验身份证号码(显示详情)

```python
>>> import pymod112
>>> pymod112.mod112('11010519491231002X', details=True, location_check=True)
{'id': '11010519491231002X',
 'province': ['11', '北京市'],
 'city': ['01', ''],
 'county': ['05', '朝阳区'],
 'birth_date': ['1949', '12', '31'],
 'gender': '女',
 'result': True,
 'problem': '000'}
```

查询地区代码对应的地区名

```python
>>> import pymod112
>>> pymod112.code2location('110105')
['北京市', '', '朝阳区']
```

查询地区名对应的地区代码

```python
>>> import pymod112
>>> pymod112.location2code(['北京市', '朝阳区'])
'110105'
```

返回全部错误代码及其对应内容

```python
>>> import pymod112
>>> pymod112.CODE2ERROR
{'000':'不存在问题',
 '001':'缺失关键文件',
 '002':'参数location长度错误',
 '003':'参数code长度错误',
 '004':'参数id长度错误',
 '005':'参数id内容包含非法字符',
 '006':'参数id不合法',
 '007':'参数id中包含不存在的地区',
 '008':'参数id中包含不存在的时间'}
```

返回区划码版本

```python
>>> import pymod112
>>> pymod112.RCLIST
["24", "20"]
```

## 许可证
MIT License

## 更新日志
### **0.1.5(2025-11-7)**
 - 错误修复
    - 更新了区划码，修复了地址检查出错的可能性
 - 新增
    - 新增可选参数rc_time，默认最新版，可选版本请查找RCLIST
    - 新增常量RCLIST，存储区划码版本，最新版本是RCLIST[0]

### **0.1.4(2024-9-21)**
 - 错误修复
     - 修复了资源缺失的问题
 - 新增
     - 新增最早出生时间检查
     - 新增错误代码'001'
     - 新增对关键资源的检查
 - 已知问题
     - 存在地址检查出错的可能性

### **0.1.2(2023-8-5)**
 - 错误修复
     - 修复了参数id来自同年的未来时间也可能通过时间校验的问题
     - 修复了参数id最后一位不合法但不会返回错误代码005的问题
 - 新增
     - 新增函数location2code以方便查询行政区划代码
 - 改进
     - 修改了一个函数名(code_to_location -> code2location)
     - 修改了一个常量名(code_to_error -> CODE2ERROR)
     - 函数code2location参数code要求类型由list变为str
     - 更新了CODE2ERROR
     - 函数mod112返回中'gender'的值变为'男'或'女'
 - 其它
    - 开源许可证更改为MIT License

### **0.1.1(2023-7-2)**
 - 加入参数类型检查
 - 优化错误代码（停用001 002 003）
 - 删除函数problem()

### **0.1.0(2023-6-24)**
- 这是第一个正式发行版

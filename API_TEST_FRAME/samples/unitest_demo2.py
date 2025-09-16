import unittest
import paramunittest


#支持元组
# @paramunittest.parametrized(
#     (8,5),
#     (10,20)
# )
#支持列表
# @paramunittest.parametrized(
#     [8,5],
#     [10,20]
# )

#支持字典
# @paramunittest.parametrized(
#     {'numa':1,'numb':5},
#     {'numa':6,'numb':10}
# )
#函数或者数据对象传入

testdata = (
    {'numa':1,'numb':5},
    {'numa':6,'numb':10}
)
@paramunittest.parametrized(
    *testdata
)

class UTestDemo(unittest.TestCase):
    def setParameters(self,numa,numb):
        self.numa = numa
        self.numb = numb

    def test_add(self):
        self.assertGreater(self.numa,self.numb)

if __name__ == '__main__':
    unittest.main()
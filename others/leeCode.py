class Solution(object):
    # 回文整数
    def isPalindrome1(self, n):
        if n < 0:
            print('0')
            return 0
        ret = 0
        x = n
        while x != 0:
            r, x = x % 10, x // 10
            ret = ret * 10 + r
        return n == ret

    # 回文整数
    def isPalindrome2(self, n):
        print(str(n)[::-1])
        return str(n)[::-1]==str(n)

    # 两数之和
    def twoSum(self, nums, target):

        hashmap = {}
        for i, j in enumerate(nums):
            a_nums = target - nums[i]
            if a_nums in hashmap:
                print(hashmap[a_nums], i)
                return [hashmap[a_nums], i]
            hashmap[j] = i
            print(hashmap)



if __name__=='__main__':
    p = Solution()
    # p.isPalindrome2(1211)
    p.twoSum([3,6,7,2,8,5,4], 6)

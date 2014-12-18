import random, string

class RandomGenerator(object) :
    def GenPassword(length=6):
        #随机出数字的个数
        numOfNum = random.randint(1,length-1)
        numOfLetter = length - numOfNum
        #选中numOfNum个数字
        slcNum = [random.choice(string.digits) for i in range(numOfNum)]
        #选中numOfLetter个字母
        slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
        #打乱这个组合
        slcChar = slcNum + slcLetter
        random.shuffle(slcChar)
        #生成密码
        genPwd = ''.join([i for i in slcChar])
        return genPwd
    
    def GenRandomNumber(length=6):
        #随机出数字的个数
        slcNum = [random.choice(string.digits) for i in range(length)]
        #打乱组合
        random.shuffle(slcChar)
        #返回
        genNumber = ''.join([i for i in slcChar])
        return genNumber
    
    def GenRandomString(length=6):
        #随机产生指字长度的字母
        slcChar = [random.choice(string.ascii_letters) for i in range(length)]
        #打乱这个组合
        random.shuffle(slcChar)
        #生成密码
        genString = ''.join([i for i in slcChar])
        return genString
    
 
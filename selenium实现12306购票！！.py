from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, ElementNotInteractableException
import csv


#这里driver放在类外面的原因是因为防止main函数执行完毕后会消除内存中的临时变量，导致类对象ribber被删除，造成网页自动关闭
driver = webdriver.Chrome(executable_path="D:\driver\chromedriver.exe")  # 谷歌浏览器
# driver = webdriver.Firefox(executable_path="D:\driver\geckodriver.exe")  # 火狐浏览器
# driver = webdriver.Edge(executable_path="D:\driver\msedgedriver.exe")  # Microsoft Edge浏览器


class TrainRibber(object):
    login_url = "https://kyfw.12306.cn/otn/resources/login.html"              #登陆界面Url
    main_page_url = "https://kyfw.12306.cn/otn/view/index.html"               #主界面url
    ticket_page_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"   #车票页面url
    order_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"                     #订单页面url
    def __init__(self, from_station, to_station, train_data, trains, passengers) :
        self.from_station = from_station                         #出发地
        self.to_station = to_station                             #目的地
        self.train_data = train_data                             #日期
        self.dic_code = {}                                       #车站代码
        self.train = None                                        #决定提交订单的火车列次
        self.trains = trains                                     #用户想要购买的车次和座位
        self.passengers = passengers                             #乘客姓名及购买的票的类型
        # 执行获取车站地点代码的函数
        self.get_station_code()

    def get_station_code(self):
        with open("stations.csv",'r',encoding="utf-8") as f:
            lines = csv.DictReader(f)
            for line in lines:
                name = line['name']
                code = line['code']
                self.dic_code[name] = code


    def login(self):
        driver.get(self.login_url)
        WebDriverWait(driver, 1000).until(
            EC.url_to_be(self.main_page_url)                      #显式等待登陆
        )
        print("登陆成功！")


    def search_ticket(self):
        driver.get(self.ticket_page_url)
        message_confirm_btn = driver.find_element_by_id("qd_closeDefaultWarningWindowDialog_id")
        message_confirm_btn.click()
        #出发地设置
        from_station_input_Tag = driver.find_element_by_id("fromStation")                                  #拿到标签
        from_station_code = self.dic_code[self.from_station]                                                #根据车站地名查询车站代码
        driver.execute_script("arguments[0].value='%s'" % from_station_code,from_station_input_Tag)           #通过JS来对标签中的值进行更改
        #目的地设置
        to_station_input_Tag = driver.find_element_by_id("toStation")
        to_station_code = self.dic_code[self.to_station]
        driver.execute_script("arguments[0].value='%s'" % to_station_code, to_station_input_Tag)
        #出发日期设置
        train_data_input_Tag = driver.find_element_by_id("train_date")
        driver.execute_script("arguments[0].value='%s'" % self.train_data, train_data_input_Tag)
        #点击查询
        search_btn = driver.find_element_by_id("query_ticket")
        search_btn.click()
        #解析车辆信息
        WebDriverWait(driver,1000).until(
            EC.presence_of_element_located((By.XPATH,"//tbody[@id='queryLeftTable']/tr"))
        )
        train_trs = driver.find_elements_by_xpath("//tbody[@id='queryLeftTable']/tr[not(@datatran)]")
        ticket_buy = False                                                     #标志选票是否成功
        while True:
            for train_tr in train_trs:
                infos = train_tr.text.replace("\n", " ").split(" ")         #将每列车的信息从字符串变成列表
                print(infos)
                if infos[0] in self.trains:                               # 判断该火车列次是否在想要乘坐的火车列次中
                    user_acceptable_seats = self.trains[infos[0]]          # 获取该火车下用户可接受的所有座位类型
                    for user_acceptable_seat in user_acceptable_seats:      # 分别判断每种座位类型是否在该车次中有余票
                        if user_acceptable_seat == "9":
                            count = infos[7]
                            if count.isdigit() or count == "有":
                                ticket_buy = True
                                break
                        elif user_acceptable_seat == "M":
                            count = infos[8]
                            if count.isdigit() or count == "有":
                                ticket_buy = True
                                break                                                 #火车座位类型 9:商务座，M：一等座，O：二等座，3：硬卧，4：软卧，1：硬座
                        elif user_acceptable_seat == "O":
                            count = infos[9]
                            if count.isdigit() or count == "有":
                                ticket_buy = True
                                break
                        elif user_acceptable_seat == "1":
                            count = infos[15]
                            if count.isdigit() or count == "有":
                                ticket_buy = True
                                break
                        elif user_acceptable_seat == "3":
                            count = infos[13]
                            if count.isdigit() or count == "有":
                                ticket_buy = True
                                break
                        elif user_acceptable_seat == "4":
                            count = infos[11]
                            if count.isdigit() or count == "有":
                                ticket_buy = True
                                break
                    if ticket_buy:
                        self.train = infos[0]
                        train_tr.find_element_by_xpath("//a[@class = 'btn72']").click()
                        return
                    else:
                        print("%s车次中没有想要乘坐的座位！" % infos[0])
            print("没有想要乘坐的车次！")


    def confirm_passengers(self):
        passenger_num = 0
        WebDriverWait(driver,1000).until(
            EC.url_to_be(self.order_url)
        )
        #等待选择乘客按钮
        WebDriverWait(driver,1000).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class = 'item clearfix']/ul/li/label"))
        )

        # 选择乘客
        passenger_labels = driver.find_elements_by_xpath("//div[@class = 'item clearfix']/ul/li/label")
        for passenger_label in passenger_labels:
            name = passenger_label.text
            if name in self.passengers.keys():                    #如果该label标签下的名字在想要购票的乘客中，就点击
                passenger_num += 1
                passenger_label.click()
                # 选择是否购买学生票
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class = 'up-box w600']"))  # 等待学生票购买提示的弹窗出现
                )
                driver.find_element_by_id("dialog_xsertcj_ok").click()  # 点击确定按钮

        # 选择票型
        for i in range(1, passenger_num+1):
            select_ages = Select(driver.find_element_by_id("ticketType_{0}".format(i)))
            age_types = self.passengers.values()
            for age_type in age_types:
                try:
                    select_ages.select_by_value(age_type)
                except NoSuchElementException:
                    continue
                else:
                    break

        #选择座位
        for i in range(1, passenger_num+1):
            select_seats = Select(driver.find_element_by_id("seatType_{0}".format(i)))
            seat_types = self.trains[self.train]                             # 获得已决定提交订单的列车下所有用户希望的座位类型
            for seat_type in seat_types:                                     # 循环判断座位类型是否在select表单中
                try:
                    select_seats.select_by_value(seat_type)
                except NoSuchElementException:                                   # 捕获不存在的错误
                    continue
                else:
                    break                                                   # 存在则退出

        #等待提交订单
        WebDriverWait(driver,1000).until(
            EC.element_to_be_clickable((By.ID,"submitOrder_id"))
        )
        #提交订单
        submit_order_btn = driver.find_element_by_id("submitOrder_id")
        submit_order_btn.click()

        #等待确认订单
        WebDriverWait(driver,1000).until(
            EC.presence_of_element_located((By.CLASS_NAME,"dhtmlx_window_active"))
        )
        WebDriverWait(driver, 1000).until(
            EC.element_to_be_clickable((By.ID,"qr_submit_id"))
        )
        #确认订单
        order_btn = driver.find_element_by_id("qr_submit_id")
        try:
            while order_btn:                                                   # 持续点击确定
                order_btn.click()
                order_btn = driver.find_element_by_id("qr_submit_id")
        except ElementNotVisibleException:
            pass
        except ElementNotInteractableException:
            pass
        print("本次12306购票测试成功！！！")



    def run(self):
        # 1. 登陆
        self.login()
        # 2. 查找余票
        self.search_ticket()
        # 3. 确认乘客及座位
        self.confirm_passengers()





def main():
    # 火车座位类型 9:商务座，M：一等座，O：二等座，3：硬卧，4：软卧，1：硬座
    # 乘客票类型： 1:成人票，2:儿童票，3：学生票，4：残军票
    from_station = input("请输入出发地： ")
    to_station = input("请输入目的地： ")
    start_time = input("请输入出发时间（格式：年-月-日）：")
    ribber = TrainRibber(from_station, to_station, start_time, {"K1064": ["O", "M", "1"]}, {"李琪旺(学生)":["1", "3"], "李含婷(学生)": ["1", "3"]})
    ribber.run()

if __name__ == '__main__':
    main()



#此代码还有诸多可以完善的地方
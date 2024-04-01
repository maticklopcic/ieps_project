class Regex:
    def __init__(self) -> None:
        #base_dir = r'C:\Users\jurea\Desktop\Faks\MAG\12\IEPS\Projekt1\ieps_project'
        self.rtv1 = r'strani\rtvslo.si\Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html'
        with open(self.rtv1, 'r', encoding='ISO-8859-1') as file:
            self.rtv1_html_content = file.read()
        self.rtv2 = r'strani\rtvslo.si\Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html'
        with open(self.rtv2, 'r', encoding='ISO-8859-1') as file:
            self.rtv2_html_content = file.read()
        self.ovs1 = r'strani\overstock.com\jewelry01.html'
        with open(self.ovs1, 'r', encoding='ISO-8859-1') as file:
            self.ovs1_html_content = file.read()
        self.ovs2 = r'strani\overstock.com\jewelry02.html'
        with open(self.ovs2, 'r', encoding='ISO-8859-1') as file:
            self.ovs2_html_content = file.read()

    def rtv(self):
        print("RTV1")
        #print(self.rtv1_html_content)
        return "regex"
    
    def overstock(self):
        print(self.ovs1_html_content)
        return "regex"
    
    def custom(self, html):
        return "regex"

from xml.etree import ElementTree

kinds = ['formula', 'figure', 'table']


class FileData:
    def __init__(self):
        self.page_lines = []
        self.filename = ''
        self.img_path = ''

    def set_image_path(self, img_path):
        self.img_path = img_path

    def get_txt_name(self):
        return self.filename.split('\\')[-1]

    def get_img_name(self):
        return self.imgpath.split('\\')[-1]

    def read_txt(self, txt_path):
        self.filename = txt_path
        self.page_lines = []
        root = ElementTree.parse(txt_path)
        for name in ['figureRegion', 'formulaRegion', 'tableRegion']:
            p = root.findall(name)
            for line in p:
                coords = line.getchildren()
                line = coords[0].attrib['points']
                line = line.split(' ')
                kinds = name.split('Region')[0]
                region = Rect(10000, 0, 10000, 0)
                for xy in line:
                    x, y = xy.split(',')
                    region.update(int(x), int(y))
                self.page_lines.append(PageLine(region, kinds))


class PageLine:
    def __init__(self, rect, kind):
        self.kind = kind
        self.rect = rect
        self.comp_list = []
        self.prob = 0

    def add_comp(self, comp):
        self.compList.append(comp)

    def show_comp(self):
        for comp_region in self.comp_list:
            print(comp_region.tostr(), ',')

    def show(self):
        print(self.rect.tostr()+'\t'+self.kind)

    def get_kind(self):
        return self.kind


class Rect:
    def __init__(self, l, r, u, d):
        self.l = int(l)
        self.r = int(r)
        self.u = int(u)
        self.d = int(d)

    def update(self, x, y):
        self.l = min(self.l, x)
        self.r = max(self.r, x)
        self.u = min(self.u, y)
        self.d = max(self.d, y)

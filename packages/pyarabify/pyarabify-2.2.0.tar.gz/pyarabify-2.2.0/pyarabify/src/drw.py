import sys

try:
    import turtle as _turtle_module
    TURTLE_AVAILABLE = True
except ImportError:
    TURTLE_AVAILABLE = False

class سلحفاة_عربية:
    def __init__(self):
        if not TURTLE_AVAILABLE:
            raise ImportError("مكتبة turtle غير متاحة. يرجى تثبيتها أولاً")
        self.سلحفاة = _turtle_module.Turtle()
        self.شاشة = _turtle_module.Screen()

    def تقدم(self, مسافة):
        self.سلحفاة.forward(مسافة)
        return self

    def تراجع(self, مسافة):
        self.سلحفاة.backward(مسافة)
        return self

    def يمين(self, زاوية):
        self.سلحفاة.right(زاوية)
        return self

    def يسار(self, زاوية):
        self.سلحفاة.left(زاوية)
        return self

    def ارسم_دائرة(self, نصف_قطر):
        self.سلحفاة.circle(نصف_قطر)
        return self

    def ارسم_مربع(self, طول):
        for _ in range(4):
            self.سلحفاة.forward(طول)
            self.سلحفاة.right(90)
        return self

    def ارسم_مستطيل(self, طول, عرض):
        for _ in range(2):
            self.سلحفاة.forward(طول)
            self.سلحفاة.right(90)
            self.سلحفاة.forward(عرض)
            self.سلحفاة.right(90)
        return self

    def ارسم_مثلث(self, طول):
        for _ in range(3):
            self.سلحفاة.forward(طول)
            self.سلحفاة.left(120)
        return self

    def ارسم_نجمة(self, عدد_الاضلاع=5, طول=100):
        زاوية = 180 - (180 / عدد_الاضلاع)
        for _ in range(عدد_الاضلاع):
            self.سلحفاة.forward(طول)
            self.سلحفاة.right(زاوية)
        return self

    def لون_القلم(self, لون):
        self.سلحفاة.pencolor(لون)
        return self

    def لون_التعبئة(self, لون):
        self.سلحفاة.fillcolor(لون)
        return self

    def ابدأ_التعبئة(self):
        self.سلحفاة.begin_fill()
        return self

    def انهي_التعبئة(self):
        self.سلحفاة.end_fill()
        return self

    def سمك_القلم(self, سمك):
        self.سلحفاة.pensize(سمك)
        return self

    def ارفع_القلم(self):
        self.سلحفاة.penup()
        return self

    def اخفض_القلم(self):
        self.سلحفاة.pendown()
        return self

    def اذهب_الى(self, س, ص):
        self.سلحفاة.goto(س, ص)
        return self

    def امسح(self):
        self.سلحفاة.clear()
        return self

    def اعد_تعيين(self):
        self.سلحفاة.reset()
        return self

    def اخف(self):
        self.سلحفاة.hideturtle()
        return self

    def اظهر(self):
        self.سلحفاة.showturtle()
        return self

    def سرعة(self, سرعة):
        self.سلحفاة.speed(سرعة)
        return self

    def انتظر(self):
        self.شاشة.mainloop()

    def اغلق(self):
        _turtle_module.bye()

def create_turtle():
    if not TURTLE_AVAILABLE:
        print("مكتبة turtle غير متاحة. لاستخدام الرسوميات، قم بتثبيت المكتبة أولاً")
        return None
    return سلحفاة_عربية()

انشئ_سلحفاة = create_turtle
سلحفاة = create_turtle

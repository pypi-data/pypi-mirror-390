ver = "0.3.3"
dver = "nop"
mod = ["music","log","flush","option"]
class option:
    def show_options():
        print("In LTPpyTools option,you can use this:")
        print("----SHOW----")
        print("show_this_ver():show ver")
        print("show_big_ver():look it alpha,beta,or build(sometimes nop)")
        print("show_mod():show mod")
        
    


    def show_this_ver():
        print({ver})


    def show_big_ver():
        print({dver})

    def show_mod():
        print(*mod)




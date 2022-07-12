from ROOT import *
#gROOT.SetBatch(kTRUE)

myfile = TFile("stuff.root")
w = myfile.Get("wdiphoton_power")
th1x=w.var("th1x")

mypdf = w.pdf("extDijetPdf") #Name of pdf in workspace
sbkg = mypdf.createHistogram("h_binned_diphoton_power", w.var('mjj'), RooFit.Binning(3100,0.,3100.)) #Create histogram from pdf

xframe=th1x.frame()
mypdf.plotOn(xframe) #This shows proper function as expected
cv = TCanvas("rfcanv","rfcanv",800,800)
xframe.Draw()
cv.Print("rfcanv.png")

cc = TCanvas("c","c",800,800)
sbkg.SetLineColor(kRed)
print(type(sbkg)) #sbkg is a TF1
sbkg.Draw() #This plots at 0
cc.Print("tfCanv.png")





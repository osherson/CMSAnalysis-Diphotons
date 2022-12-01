#
import ROOT
RDF = ROOT.ROOT.RDataFrame
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from ROOT import *
import sys,os
import glob
import time

nbins_dipho = 400*4/10
dipho_low = 0
dipho_high = 4

Chain = TChain("pico_tree")
#Chain.Add("PicoTrees/data_16.root")
#Chain.Add("PicoTrees/data_17.root")
Chain.Add("PicoTrees/data_18.root")
Rdf = RDF(Chain)


### 
# Pass Plots
isohist = Rdf.Histo1D(("clu1_iso","Cluster Energy / Jet Energy; Isolation; Events", 100, 0, 1.1),'clu1_iso')

#energyhist_pp = Rdf.Histo1D(("energy_pp","Cluster Energy, pass; Energy (GeV); Events",100, 25, 65), 'energy_iso_pp', 'nWgt')
#etahist_pp = Rdf.Histo1D(("eta_pp","Cluster #eta, pass; #eta; Events",100, -2, 2), 'eta_iso_pp', 'nWgt')
#phihist_pp = Rdf.Histo1D(("phi_pp","Cluster #phi, pass; #phi; Events",100, -4, 4), 'phi_iso_pp', 'nWgt')
##drhist_pp = Rdf.Histo1D(("dr_pp","#Delta R to Nearest Jet, pass; #Delta R; Events", 100, 0, 1),'nj_dr_pp', 'nWgt')
##rathist_pp = Rdf.Histo1D(("eratio_pp","Cluster Energy / Jet Energy, pass; Energy Ratio; Events", 100, 0, 2),'eratio_pp', 'nWgt')
##2d
#twoD_CluE_pp = Rdf.Histo2D(("energytwod_pp"," Cluster Energy vs. Diphoton Mass pass; Mass (GeV); Energy (GeV)", nbins_dipho, dipho_low, dipho_high, 100, 25, 65),"ClusterMass_pp","ruclu_energy_pp", "nWgt")
#twoD_deltaR_pp = Rdf.Histo2D(("drtwod_pp"," #Delta R(Cluster, Nearest Jet) vs. Diphoton Mass pass; Mass (GeV); #DeltaR", nbins_dipho, dipho_low, dipho_high, 100, 0, 0.45),"ClusterMass_pp","nj_dr_pp", "nWgt")

twoD_masym = Rdf.Histo2D(("masymtwod"," Mass Asymmetry vs. Diphoton Mass; Mass (GeV); Isolation", nbins_dipho, dipho_low, dipho_high, 100, 0, 1.1),"clu1_mass","masym")
Rdf = Rdf.Filter("masym > 0.85 ", "Mass Asymmetry")
twoD_iso = Rdf.Histo2D(("isotwod"," Isolation vs. Diphoton Mass; Mass (GeV); Isolation", nbins_dipho, 0., 2., 100, 0.2, 1.0),"clu1_mass","clu1_iso")
twoD_dipho = Rdf.Histo2D(("diphotwod"," Diphoton Score vs. Diphoton Mass; Mass (GeV); Isolation", nbins_dipho, dipho_low, dipho_high, 100, 0, 1.1),"clu1_mass","clu1_dipho")
twoD_deta = Rdf.Histo2D(("detatwod"," #Delta #eta vs. Diphoton Mass; Mass (GeV); Isolation", nbins_dipho, dipho_low, dipho_high, 100, 0, 3.5),"clu1_mass","deta")

Rdf = Rdf.Filter("clu1_iso > 0.4 && clu1_iso < 0.8", "Isolation")
rr = Rdf.Report()
rr.Print()
masshist = Rdf.Histo1D(("clu1_mass","Diphoton Mass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'clu1_mass')
twoD_iso_pc = Rdf.Histo2D(("isotwod_pc"," Isolation vs. Diphoton Mass; Mass (GeV); Isolation", nbins_dipho, dipho_low, dipho_high, 100, 0, 1.1),"clu1_mass","clu1_iso")

oF = TFile("PlotFiles/plots_18.root", "recreate")
oF.cd()
masshist.GetValue().Write()
isohist.GetValue().Write()
twoD_iso.GetValue().Write()
twoD_dipho.GetValue().Write()
twoD_masym.GetValue().Write()
twoD_deta.GetValue().Write()
twoD_iso_pc.GetValue().Write()

oF.Write()
oF.Save()
oF.Close()

#tf = time.time()
#print("Run time: {} min".format( (tf-ts) / 60 ))

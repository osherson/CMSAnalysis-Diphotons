#include <vector>
#include <stdexcept>
#include <string>
#include <algorithm>
#include <iostream>
#include <cmath>
#include "ROOT/RVec.hxx"

using namespace ROOT::VecOps;
using rvec_f = const RVec<float> &;

static const float DIPHO_THRESH = 0.9;
//static const float DIPHO_THRESH = 0.5;
//static const float DIPHO_THRESH = 0.9;

int getSign(float num){
  if(num < 0){return -1.;}
  else{return 1;}
}

float ZShift(float eta, float zPV){

  float R = 129.;
  float theta = 2.*TMath::ATan(TMath::Exp(-1.*abs(eta)));
  float z = R / TMath::Tan(theta) * getSign(eta);
  float zp;
  float thetaprime;
  float etaprime = 0.;

  if (zPV < 0 && z >= 0){
      zp = abs(zPV) + abs(z);
      thetaprime = TMath::ATan(R/zp);
      etaprime = -1. * TMath::Log(TMath::Tan(thetaprime/2.));
      return etaprime;
  }
  if (zPV >= 0 && z < 0){
      zp = abs(zPV) + abs(z);
      thetaprime = TMath::ATan(R/zp);
      etaprime = TMath::Log(TMath::Tan(thetaprime/2.));
      return etaprime;
  }

  if (zPV >= 0 && z >= 0 && z > zPV){
      zp = abs(z) - abs(zPV);
      thetaprime = TMath::ATan(R/zp);
      etaprime = -1. * TMath::Log(TMath::Tan(thetaprime/2.));
      return etaprime;
  }
  if (zPV < 0 && z < 0 && z < zPV){
      zp = abs(z) - abs(zPV);
      thetaprime = TMath::ATan(R/zp);
      etaprime = TMath::Log(TMath::Tan(thetaprime/2.));
      return etaprime;
  }

  if (zPV >= 0 && z >= 0 && z < zPV){
      zp = abs(zPV) - abs(z);
      thetaprime = TMath::ATan(R/zp);
      etaprime = TMath::Log(TMath::Tan(thetaprime/2.));
      return etaprime;
  }
  if (zPV < 0 && z < 0 && z >= zPV){
      zp = abs(zPV) - abs(z);
      thetaprime = TMath::ATan(R/zp);
      etaprime = -1.*TMath::Log(TMath::Tan(thetaprime/2.));
      return etaprime;
  }

  return etaprime;

}

RVec<float> getMatchedClusterMass(rvec_f ruclu_eta, rvec_f ruclu_phi, rvec_f ruclu_energy, rvec_f moe, rvec_f jet_pt, rvec_f jet_eta, rvec_f jet_phi, rvec_f jet_mass, rvec_f jet_energy, rvec_f jet_matchedEtaE){

  RVec<float> Es;
  //or (unsigned int ii=0; ii<ruclu_eta.size(); ii++){
  // Es.push_back(-999.);
  //}

  for(unsigned int j=0; j< jet_pt.size(); j++){
    if(jet_matchedEtaE.at(j) < 30 || jet_matchedEtaE.at(j) > 60){continue;}
    TLorentzVector jet;
    jet.SetPtEtaPhiM( jet_pt.at(j), jet_eta.at(j), jet_phi.at(j), jet_mass.at(j));

    float min_dr = 1000.;
    float useE = -999.;

    for(unsigned int clu_index=0; clu_index < ruclu_eta.size(); clu_index++){
      TLorentzVector cluster;
      float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1* ruclu_eta.at(clu_index) ) ) * 2 );
      cluster.SetPtEtaPhiM( c_pt, ruclu_eta.at(clu_index), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );
      if(cluster.DeltaR( jet ) < min_dr){
        min_dr = cluster.DeltaR( jet );
        useE = ruclu_energy.at(clu_index) * moe.at(clu_index);
        }
      }
      Es.push_back(useE);
  }
  return Es;
}

RVec<float> getMatchedClusterParam(rvec_f ruclu_eta, rvec_f ruclu_phi, rvec_f ruclu_energy, rvec_f moe, rvec_f jet_pt, rvec_f jet_eta, rvec_f jet_phi, rvec_f jet_mass, rvec_f jet_energy, rvec_f jet_matchedEtaE, rvec_f param){

  RVec<float> Es;
  //or (unsigned int ii=0; ii<ruclu_eta.size(); ii++){
  // Es.push_back(-999.);
  //}

  for(unsigned int j=0; j< jet_pt.size(); j++){
    if(jet_matchedEtaE.at(j) < 30 || jet_matchedEtaE.at(j) > 60){continue;}
    TLorentzVector jet;
    jet.SetPtEtaPhiM( jet_pt.at(j), jet_eta.at(j), jet_phi.at(j), jet_mass.at(j));

    float min_dr = 1000.;
    float useE = -999.;

    for(unsigned int clu_index=0; clu_index < ruclu_eta.size(); clu_index++){
      TLorentzVector cluster;
      float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1* ruclu_eta.at(clu_index) ) ) * 2 );
      cluster.SetPtEtaPhiM( c_pt, ruclu_eta.at(clu_index), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );
      if(cluster.DeltaR( jet ) < min_dr){
        min_dr = cluster.DeltaR( jet );
        useE = param.at(clu_index);
        }
      }
      Es.push_back(useE);
  }
  return Es;
}

int getMax(rvec_f myvec){
  int m = std::distance(myvec.begin(), std::max_element(myvec.begin(), myvec.end()) );
  return m;
}

//int getnMax(rvec_f myvec){
//  myvec = myvec.erase(std::max_element(myvec.begin(), myvec.end()) );
//  return std::distance(myvec.begin(), std::max_element(myvec.begin(), myvec.end()) );
//}


RVec<float> getClosestJetEn(rvec_f ruclu_eta, rvec_f ruclu_phi, rvec_f ruclu_energy, rvec_f moe, rvec_f jet_pt, rvec_f jet_eta, rvec_f jet_phi, rvec_f jet_mass, rvec_f jet_energy){

  RVec<float> Es;
  for (unsigned int ii=0; ii<ruclu_eta.size(); ii++){
    Es.push_back(-999.);
  }

  for(unsigned int clu_index=0; clu_index < ruclu_eta.size(); clu_index++){
    TLorentzVector cluster;
    //float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1*ZShift( ruclu_eta.at(clu_index), 0. ) ) ) * 2 );
    //cluster.SetPtEtaPhiM( c_pt, ZShift(ruclu_eta.at(clu_index), 0.), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );

    float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1* ruclu_eta.at(clu_index) ) ) * 2 );
    cluster.SetPtEtaPhiM( c_pt, ruclu_eta.at(clu_index), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );

    float min_dr = 1000.;
    float useE = -999.;

    for(unsigned int j=0; j< jet_pt.size(); j++){
      TLorentzVector jet;
      jet.SetPtEtaPhiM( jet_pt.at(j), jet_eta.at(j), jet_phi.at(j), jet_mass.at(j));
      if(cluster.DeltaR( jet ) < min_dr){
        min_dr = cluster.DeltaR( jet );
        useE = jet_energy.at(j);
        }
      }
    Es.at(clu_index) = useE;
    }

  return Es;
}

RVec<float> getClosestJetDR(rvec_f ruclu_eta, rvec_f ruclu_phi, rvec_f ruclu_energy, rvec_f moe, rvec_f jet_pt, rvec_f jet_eta, rvec_f jet_phi, rvec_f jet_mass){

  RVec<float> Es;
  for (unsigned int ii=0; ii<ruclu_eta.size(); ii++){
    Es.push_back(-999.);
  }

  for(unsigned int clu_index=0; clu_index < ruclu_eta.size(); clu_index++){
    TLorentzVector cluster;
    //float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1*ZShift( ruclu_eta.at(clu_index), 0. ) ) ) * 2 );
    //cluster.SetPtEtaPhiM( c_pt, ZShift(ruclu_eta.at(clu_index), 0.), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );

    float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1* ruclu_eta.at(clu_index) ) ) * 2 );
    cluster.SetPtEtaPhiM( c_pt, ruclu_eta.at(clu_index), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );

    float min_dr = 1000.;
    float useE = -999.;

    for(unsigned int j=0; j< jet_pt.size(); j++){
      TLorentzVector jet;
      jet.SetPtEtaPhiM( jet_pt.at(j), jet_eta.at(j), jet_phi.at(j), jet_mass.at(j));
      if(cluster.DeltaR( jet ) < min_dr){
        min_dr = cluster.DeltaR( jet );
        }
      }
    Es.at(clu_index) = min_dr;
    }

  return Es;
}

RVec<float> getClosestJet(rvec_f ruclu_eta, rvec_f ruclu_phi, rvec_f ruclu_energy, rvec_f moe, rvec_f jet_pt, rvec_f jet_eta, rvec_f jet_phi, rvec_f jet_mass){

  RVec<float> minDrs;
  for (unsigned int ii=0; ii<ruclu_eta.size(); ii++){
    minDrs.push_back(1000.);
  }
  
  for(unsigned int clu_index=0; clu_index < ruclu_eta.size(); clu_index++){
    TLorentzVector cluster;
    //float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1*ZShift( ruclu_eta.at(clu_index), 0. ) ) ) * 2 );
    //cluster.SetPtEtaPhiM( c_pt, ZShift(ruclu_eta.at(clu_index), 0.), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );

    float c_pt = ruclu_energy.at(clu_index) * TMath::Sin(TMath::ATan(TMath::Exp(-1* ruclu_eta.at(clu_index) ) ) * 2 );
    cluster.SetPtEtaPhiM( c_pt, ruclu_eta.at(clu_index), ruclu_phi.at(clu_index), ruclu_energy.at(clu_index)*moe.at(clu_index) );

    float min_dr = 1000.;

    for(unsigned int j=0; j< jet_pt.size(); j++){
      TLorentzVector jet;
      jet.SetPtEtaPhiM( jet_pt.at(j), jet_eta.at(j), jet_phi.at(j), jet_mass.at(j));
      if(cluster.DeltaR( jet ) < min_dr){
        min_dr = cluster.DeltaR( jet );
        }
      }

    minDrs.at(clu_index) = min_dr;
    }

  return minDrs;
}

int convertTriggers(rvec_f triggers){

  for(unsigned int jj=0; jj<triggers.size(); jj++){
    std::cout << triggers.at(jj) << std::endl;
  }
  
  return 0;
}

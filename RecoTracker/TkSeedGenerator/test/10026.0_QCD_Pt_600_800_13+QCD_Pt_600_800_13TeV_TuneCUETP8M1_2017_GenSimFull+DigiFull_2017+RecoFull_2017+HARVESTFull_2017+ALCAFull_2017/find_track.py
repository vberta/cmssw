#! /usr/bin/env python
import ROOT
import sys
from DataFormats.FWLite import Events, Handle

events = Events (['step3.root'])

handleT  = Handle ("std::vector<reco::Track>")
labelT = ("generalTracks")

ROOT.gROOT.SetBatch()        # don't pop up canvases
ROOT.gROOT.SetStyle('Plain') # white background

for event in events:
    event.getByLabel (labelT, handleT)
    tracks = handleT.product()

    for t in tracks  :
        # print t.pt(),t.eta(),t.algo()
        if t.algo() == 11 :
             print t.pt(),t.eta(),t.phi(),t.algo()
             print "inner det ID=", t.innerDetId()
             print "vertex", t.vertex().x(), t.vertex().y(), t.vertex().z()
             print "seedDirection=", t.seedDirection()
             print "positon=", t.innerPosition().x(), t.innerPosition().y(), t.innerPosition().z()
             print "direction=", t.innerMomentum().x(), t.innerMomentum().y(), t.innerMomentum().z()
             print "TROVATA "
            #  exit(1)

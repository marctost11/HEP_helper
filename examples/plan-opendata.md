# The acquiring open data Phase

In this phase the data is fetched from the ATLAS open dataset.

The open data is accessed using the atlasopenmagic package. Both monte carlo datasets and data can be acquired. 

In this phase you must identify all the variables that should be extracted from the dataset. The available keys are as follows: ['num_events', 'sum_of_weights', 'sum_of_weights_squared', 'category', 'TriggerMatch_DILEPTON', 'ScaleFactor_MLTRIGGER', 'ScaleFactor_PILEUP', 'ScaleFactor_FTAG', 'mcWeight', 'xsec', 'filteff', 'kfac', 'channelNumber', 'eventNumber', 'runNumber', 'trigML', 'trigP', 'trigDT', 'trigT', 'trigE', 'trigDM', 'trigDE', 'trigM', 'trigMET', 'ScaleFactor_BTAG', 'ScaleFactor_JVT', 'jet_n', 'jet_pt', 'jet_eta', 'jet_phi', 'jet_e', 'jet_btag_quantile', 'jet_jvt', 'largeRJet_n', 'largeRJet_pt', 'largeRJet_eta', 'largeRJet_phi', 'largeRJet_e', 'largeRJet_m', 'largeRJet_D2', 'jet_pt_jer1', 'jet_pt_jer2', 'ScaleFactor_ELE', 'ScaleFactor_MUON', 'ScaleFactor_LepTRIGGER', 'ScaleFactor_MuTRIGGER', 'ScaleFactor_ElTRIGGER', 'lep_n', 'lep_type', 'lep_pt', 'lep_eta', 'lep_phi', 'lep_e', 'lep_charge', 'lep_ptvarcone30', 'lep_topoetcone20', 'lep_z0', 'lep_d0', 'lep_d0sig', 'lep_isTightID', 'lep_isMediumID', 'lep_isLooseID', 'lep_isTightIso', 'lep_isLooseIso', 'lep_isTrigMatched', 'ScaleFactor_PHOTON', 'photon_n', 'photon_pt', 'photon_eta', 'photon_phi', 'photon_e', 'photon_ptcone20', 'photon_topoetcone40', 'photon_isLooseID', 'photon_isTightID', 'photon_isLooseIso', 'photon_isTightIso', 'ScaleFactor_TAU', 'ScaleFactor_TauTRIGGER', 'ScaleFactor_DiTauTRIGGER', 'tau_n', 'tau_pt', 'tau_eta', 'tau_phi', 'tau_e', 'tau_charge', 'tau_nTracks', 'tau_isTight', 'tau_RNNJetScore', 'tau_RNNEleScore', 'truth_jet_n', 'truth_jet_pt', 'truth_jet_eta', 'truth_jet_phi', 'truth_jet_m', 'truth_elec_n', 'truth_elec_pt', 'truth_elec_eta', 'truth_elec_phi', 'truth_muon_n', 'truth_muon_pt', 'truth_muon_eta', 'truth_muon_phi', 'truth_tau_n', 'truth_tau_pt', 'truth_tau_eta', 'truth_tau_phi', 'truth_photon_n', 'truth_photon_pt', 'truth_photon_eta', 'truth_photon_phi', 'truth_met', 'truth_met_phi', 'met', 'met_phi', 'met_mpx', 'met_mpy']. All variables should be converted to awkward arrays. Make sure to use the lep_type variable when attempting to access electrons or muons specifically.

Here is an example code snipped that shows how to load a single data file and convert to awkward. Make sure to loop over all files when providing code:

```python
import atlasopenmagic as atom
import uproot


atom.set_release('2025e-13tev-beta')
skim = 'noskim'
files_list = atom.get_urls('data', skim, protocol='https', cache=True)

tree = uproot.open(files_list[0]+":analysis")
lep_pt = tree['lep_pt'].array(library="ak")
```

Here is an example output:

== Start Example Response ==

## Phase Open data acquisition

* Dataset(s)
  * <dataset-1>
* Jet Collection
  * What: pt, eta, phi
  * Filter: Jets can be filtered to be 15 GeV or better, and with eta < 1.5
* Electron Collection
  * What: pt, eta, phi
  * Filter: None

== End Example Response ==

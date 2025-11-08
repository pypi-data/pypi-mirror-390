import numpy as np
import math
import pytest
import pathlib
import tempfile
from dataclasses import asdict
from rdworks import State, StateEnsemble, StateNetwork


@pytest.fixture(scope='module') # Runs once for every test module (file).
def prepared_sm07_state():
    smiles = 'c1ccc(CNc2ncnc3ccccc23)cc1' # SAMPL6 challenge SM07
    st = State(smiles=smiles)
    return st


@pytest.fixture(scope='module')
def prepared_sm07_state_ensemble():
    smiles = 'c1ccc(CNc2ncnc3ccccc23)cc1'
    sn = StateNetwork()
    sn.build(smiles=smiles, max_formal_charge=3, tautomer_rule=None)
    assert len(sn.visited_states) == 12
    assert len(sn.graph.nodes()) == 12
    se = sn.get_state_ensemble()
    return se 


def test_state_serialize(prepared_sm07_state):
    st = prepared_sm07_state
    serialized = st.serialize()
    st2 = State().deserialize(serialized)
    assert st.smiles == st2.smiles
    assert len(st.sites) == len(st2.sites)
    assert st.origin == st2.origin
    assert st.transformation == st2.transformation
    assert st.tautomer_rule == st2.tautomer_rule
    assert st.charge == st2.charge


def test_site(prepared_sm07_state):
    """Ionizable site"""
    st = prepared_sm07_state
    assert st.site_info() == [
        ('N', 5, 0, True, True),
        ('N', 7, 0, True, False), 
        ('N', 9, 0, True, False), 
        ]
    # SMILES: c1ccc(CNc2ncnc3ccccc23)cc1
    # Formal charge: 0
    # Origin: None
    # Transformation: None
    # Ionizable sites:
    # - atom_idx=  5, atom=  N, q= +0, hs= 1, pr= 1, de= 1, acid_base= B:A:A, name= Amine:Amide:Amide vinylogue
    # - atom_idx=  7, atom=  N, q= +0, hs= 0, pr= 1, de= 0, acid_base= B, name= Aza-aromatics
    # - atom_idx=  9, atom=  N, q= +0, hs= 0, pr= 1, de= 0, acid_base= B, name= Aza-aromatics
    
    smiles = 'C1=Nc2ccccc2C(N=Cc2ccccc2)N1'
    st = State(smiles=smiles)
    assert st.site_info() == [
        ('N', 1, 0, True, False), 
        ('N', 9, 0, True, False), 
        ('N', 17, 0, True, True)]
    # SMILES: C1=Nc2ccccc2C(N=Cc2ccccc2)N1
    # Formal charge: 0
    # Origin: None
    # Transformation: None
    # Ionizable sites:
    # - atom_idx=  1, atom=  N, q= +0, hs= 0, pr= 1, de= 0, acid_base= B, name= Imine
    # - atom_idx=  9, atom=  N, q= +0, hs= 0, pr= 1, de= 0, acid_base= B, name= Imine
    # - atom_idx= 17, atom=  N, q= +0, hs= 1, pr= 1, de= 1, acid_base= A, name= Amide


def test_tautomers():
    smiles = 'c1ccc(CNc2ncnc3ccccc23)cc1'
    st1 = State(smiles=smiles, tautomer_rule='rdkit')
    se1 = StateEnsemble(st1.get_tautomers())
    assert se1.size() == 2
    st2 = State(smiles=smiles, tautomer_rule='comprehensive')
    se2 = StateEnsemble(st2.get_tautomers()) 
    assert se2.size() == 20


def test_protonate(prepared_sm07_state):
    st = prepared_sm07_state
    ps = st.get_protonated(atom_idx=9)
    assert len(ps) == 1
    assert ps[0].site_info() == [
        ('N', 5, 0, True, True),
        ('N', 7, 0, True, False), 
        ('N', 9, 1, False, True),
        ]
    # SMILES: c1ccc(CNc2nc[nH+]c3ccccc23)cc1
    # Formal charge: 1
    # Origin: c1ccc(CNc2ncnc3ccccc23)cc1
    # Transformation: +H
    # Ionizable sites:
    # - atom_idx=  5, atom=  N, q= +0, hs= 1, pr= 1, de= 1, acid_base= B:A:A, name= Amine:Amide:Amide vinylogue
    # - atom_idx=  7, atom=  N, q= +0, hs= 0, pr= 1, de= 0, acid_base= B, name= Aza-aromatics
    # - atom_idx=  9, atom=  N, q= +1, hs= 1, pr= 0, de= 1, acid_base= A, name= Aza-aromatics

    ps = st.get_protonated(site_idx=2)
    assert len(ps) == 1
    assert ps[0].site_info() == [
        ('N', 5, 0, True, True),
        ('N', 7, 0, True, False), 
        ('N', 9, 1, False, True),
        ]

    se = StateEnsemble(st.get_protonated())
    assert se.size() == 3
    results = [_.smiles for _ in se]
    expected = ['c1ccc(C[NH2+]c2ncnc3ccccc23)cc1',
                'c1ccc(CNc2[nH+]cnc3ccccc23)cc1',
                'c1ccc(CNc2nc[nH+]c3ccccc23)cc1'
                ]
    assert set(results) == set(expected)


def test_deprotonate(prepared_sm07_state):
    st = prepared_sm07_state
    des = st.get_deprotonated(atom_idx=5)
    assert len(des) == 1
    assert des[0].site_info() == [
        ('N', 5, -1, True, False),
        ('N', 7, 0, True, False), 
        ('N', 9, 0, True, False),
    ]

    des = st.get_deprotonated(site_idx=0)
    assert len(des) == 1
    assert des[0].site_info() == [
        ('N', 5, -1, True, False),
        ('N', 7, 0, True, False), 
        ('N', 9, 0, True, False),
    ]

    des = st.get_deprotonated(atom_idx=7)
    assert len(des) == 0

    se = StateEnsemble(st.get_deprotonated())
    assert se.size() == 1
    results = [_.smiles for _ in se]
    expected = ['c1ccc(C[N-]c2ncnc3ccccc23)cc1']
    assert set(results) == set(expected)

    
def test_unipka_workflow():
    smiles = 'c1ccc(CNc2ncnc3ccccc23)cc1'
    sn = StateNetwork()
    sn.build(smiles=smiles, max_formal_charge=3, tautomer_rule=None)
    assert len(sn.visited_states) == 12
    assert len(sn.graph.nodes()) == 12

    serialized = sn.serialize()
    sn2 = StateNetwork().deserialize(serialized)
    assert sn2.size() ==sn.size()
    assert sn2.get_num_nodes() == sn.get_num_nodes()
    assert sn2.get_num_edges() == sn.get_num_edges()
    assert sn2.get_initial_state() == sn.get_initial_state()
    assert sn2.get_state_ensemble() == sn.get_state_ensemble()
    
    sn.info()
    sn.get_initial_state().info()
    sn.get_state_ensemble().info()

    assert sn.get_num_nodes() == sn.get_state_ensemble().size()

    # calculated from Uni-pKa
    # Uni-pka model specific variable for pH dependent deltaG
    # Training might be conducted with a dataset in which raw pKa values
    # were subtracted by the mean value (TRANSLATE_PH).
    dG = np.array([-6.025253772735596, -2.9201512336730957, -2.7405877113342285, 
          -2.9639060497283936, 7.656927108764648, 19.67357063293457, 
          21.269811630249023, 11.911577224731445, 7.5623698234558105, 
          10.144123077392578, 21.36874008178711, 12.132856369018555])
    
    sn.set_energies(dG, ref_ph=6.504894871171601)
    se = sn.get_state_ensemble()

    se2 = StateEnsemble([st for st in sn.get_state_ensemble()])
    assert se.size() == se2.size()
    assert se == se2
    assert all(math.isclose(x, y) for x, y in zip([st.energy for st in se], [st.energy for st in se2]))


    # serialize & deserialize
    se_serialized = se.serialize()
    se3 = StateEnsemble().deserialize(se_serialized)
    assert se.size() == se3.size()
    assert se == se3
    assert all(math.isclose(x, y) for x, y in zip([st.energy for st in se], [st.energy for st in se3]))

    # population
    ph_values = np.array([1.2, 7.4, 14.0])
    p = sn.get_population(ph_values, C=math.log(10), beta=1.0)
    expected_p = [
        [2.6935020358203173e-05, 0.983819163640424, 0.027227135908720494], 
        [0.24360336373466238, 0.005614114302596941, 3.9027248338257366e-11], 
        [0.20356346464419176, 0.0046913496629296765, 3.2612529504798934e-11], 
        [0.25449881002178604, 0.005865212152380097, 4.077278781474373e-11], 
        [1.5251999407276225e-16, 8.829269017020774e-06, 0.9727728271965177], 
        [7.57267676610138e-06, 1.1011522978789083e-13, 1.9227998109993388e-28], 
        [1.534655014453089e-06, 2.2315608440876436e-14, 3.89668602382293e-29], 
        [0.01779263728460303, 2.5872494015551734e-10, 4.517778939299372e-25], 
        [3.382885964170599e-11, 1.2356211340110039e-06, 3.419574022416676e-08], 
        [2.5588578837852876e-12, 9.346395100583787e-08, 2.5866091967405752e-09], 
        [0.2805056112545945, 2.5735909639257094e-15, 1.1288239220348465e-36], 
        [7.067163565804634e-08, 1.6287075615586162e-09, 1.1322173195857867e-17]
        ]
   
    for x, y in zip(p, expected_p):
        for xz, yz in zip(x, y):
            assert math.isclose(xz, yz, abs_tol=1e-6)

    print("\n")
    for k, st in enumerate(sn.visited_states):
        print(f"{k:2} {st.smiles:50} {dG[k]:8.3f} {p[k]}")

    # population chart
    pH = np.linspace(0, 14, 60)
    p = sn.get_population(ph_values=pH, C=math.log(10), beta=1.0)

    plot_data, populated_state_idx = sn.get_plot_data_pH_vs_population(pH, p)
    
    print(f"Number of populated states: {len(populated_state_idx)}")
    print(f"Populated states (index in the state ensemble): {populated_state_idx}")
    assert min(plot_data['microstate']) == 1
    assert max(plot_data['microstate']) == len(populated_state_idx)
    assert len(plot_data['microstate']) == len(plot_data['pH'])
    assert len(plot_data['microstate']) == len(plot_data['p'])


def test_trim_and_sort():
    smiles = 'c1ccc(CNc2ncnc3ccccc23)cc1'
    sn = StateNetwork()
    sn.build(smiles=smiles, max_formal_charge=3, tautomer_rule=None)
    dG = np.array([-6.025253772735596, -2.9201512336730957, -2.7405877113342285, 
          -2.9639060497283936, 7.656927108764648, 19.67357063293457, 
          21.269811630249023, 11.911577224731445, 7.5623698234558105, 
          10.144123077392578, 21.36874008178711, 12.132856369018555])
    
    sn.set_energies(dG, ref_ph=6.504894871171601)
    se = sn.get_state_ensemble()

    assert sn.size() == 12
    assert se.size() == 12

    ph_values = np.linspace(0.0, 14.0, 60)
    p = sn.get_population(ph_values, C=math.log(10), beta=1.0)
    
    sn.trim(p, threshold=0.05)
    assert sn.size() == 6

    se.trim(p, threshold=0.05)
    assert se.size() == 6

    physiological_pH = np.array([7.4])

    p74 = se.get_population(ph_values=physiological_pH)
    assert np.allclose(p74, np.array([[9.83820473e-01],
                                   [5.61412177e-03], 
                                   [4.69135591e-03],
                                   [5.86521996e-03],
                                   [8.82928077e-06],
                                   [2.57359439e-15]]))
    
    se.sort(p74)
    assert se.size() == 6
    p74_ = se.get_population(ph_values=physiological_pH)
    assert np.allclose(p74_, np.array([[9.83820473e-01],
                                    [5.86521996e-03],
                                    [5.61412177e-03],
                                    [4.69135591e-03],
                                    [8.82928077e-06],
                                    [2.57359439e-15]]))


def test_macropka(prepared_sm07_state_ensemble):
    se = prepared_sm07_state_ensemble

    # calculated from Uni-pKa
    # Uni-pka model specific variable for pH dependent deltaG
    # Training might be conducted with a dataset in which raw pKa values
    # were subtracted by the mean value (TRANSLATE_PH).
    dG = np.array([
        -6.025253772735596, 
        -2.9201512336730957, 
        -2.7405877113342285, 
          -2.9639060497283936, 
          7.656927108764648, 
          19.67357063293457, 
          21.269811630249023, 
          11.911577224731445, 
          7.5623698234558105, 
          10.144123077392578, 
          21.36874008178711, 
          12.132856369018555])
    
    se.set_energies(dG, ref_ph=6.504894871171601)

    assert se.get_charge_groups() == {-1: [4], 0: [0, 8, 9], 1: [1, 2, 3, 11], 2: [5, 6, 7], 3: [10]}

    ph_values = np.linspace(-5, 20, 250)
    p = se.get_population(ph_values, C=math.log(10), beta=1.0)

    # population should be the same regardless of ref_state_idx
    # p_1 = se.get_population(ph_values, C=LN10, beta=1.0, ref_state_idx=1)
    # p_2 = se.get_population(ph_values, C=LN10, beta=1.0, ref_state_idx=2)
    # for x, y, z in zip(p, p_1, p_2):
    #     for xx, yy, zz in zip(x, y, z):
    #         assert math.isclose(xx, yy, abs_tol=0.01)
    #         assert math.isclose(xx, zz, abs_tol=0.01)

    # calculated macro pKa should be within 1 pH unit.
    macro_pKa = se.get_macro_pKa(ph_values, p)
    expt_macro_pKa = 6.08
    print(f"\nexpt={expt_macro_pKa} calc={macro_pKa}")
    assert any([math.isclose(x, expt_macro_pKa, abs_tol=0.8) for x,y in macro_pKa])

    # build state ensemble manually
    # reference: 
    # https://github.com/samplchallenges/SAMPL6/blob/master/physical_properties/pKa/microstates/SM07_microstates.csv
    # microstate ID	canonical isomeric SMILES	canonical SMILES
    # SM07_micro002	c1ccc(cc1)CN=c2c3ccccc3[nH]cn2	c1ccc(cc1)CN=c2c3ccccc3[nH]cn2
    # SM07_micro003	c1ccc(cc1)C/N=c\2/c3ccccc3nc[nH]2	c1ccc(cc1)CN=c2c3ccccc3nc[nH]2
    # SM07_micro004	c1ccc(cc1)CNc2c3ccccc3ncn2	c1ccc(cc1)CNc2c3ccccc3ncn2
    # SM07_micro006	c1ccc(cc1)C/[NH+]=c/2\c3ccccc3[nH]cn2	c1ccc(cc1)C[NH+]=c2c3ccccc3[nH]cn2
    # SM07_micro007	c1ccc(cc1)CNc2c3ccccc3nc[nH+]2	c1ccc(cc1)CNc2c3ccccc3nc[nH+]2
    # SM07_micro011	c1ccc(cc1)C[NH2+]c2c3ccccc3ncn2	c1ccc(cc1)C[NH2+]c2c3ccccc3ncn2
    # SM07_micro012	c1ccc(cc1)C[N-]c2c3ccccc3ncn2	c1ccc(cc1)C[N-]c2c3ccccc3ncn2
    # SM07_micro013	c1ccc(cc1)C[NH2+]c2c3ccccc3[nH+]cn2	c1ccc(cc1)C[NH2+]c2c3ccccc3[nH+]cn2
    # SM07_micro014	c1ccc(cc1)CNc2c3ccccc3[nH+]c[nH+]2	c1ccc(cc1)CNc2c3ccccc3[nH+]c[nH+]2
    # SM07_micro015	c1ccc(cc1)C[NH2+]c2c3ccccc3nc[nH+]2	c1ccc(cc1)C[NH2+]c2c3ccccc3nc[nH+]2
    # SM07_micro016	c1ccc(cc1)C[NH2+]c2c3ccccc3[nH+]c[nH+]2	c1ccc(cc1)C[NH2+]c2c3ccccc3[nH+]c[nH+]2
    states = []
    for smiles in [
        'c1ccc(cc1)CN=c2c3ccccc3[nH]cn2',
        'c1ccc(cc1)CN=c2c3ccccc3nc[nH]2',
        'c1ccc(cc1)CNc2c3ccccc3ncn2',
        'c1ccc(cc1)C[NH+]=c2c3ccccc3[nH]cn2',
        'c1ccc(cc1)CNc2c3ccccc3nc[nH+]2',
        'c1ccc(cc1)C[NH2+]c2c3ccccc3ncn2',
        'c1ccc(cc1)C[N-]c2c3ccccc3ncn2',
        'c1ccc(cc1)C[NH2+]c2c3ccccc3[nH+]cn2',
        'c1ccc(cc1)CNc2c3ccccc3[nH+]c[nH+]2',
        'c1ccc(cc1)C[NH2+]c2c3ccccc3nc[nH+]2',
        'c1ccc(cc1)C[NH2+]c2c3ccccc3[nH+]c[nH+]2',
        ]:
        states.append(State(smiles=smiles))
        
    sem = StateEnsemble(states)
    sem.info()




def test_micropka(prepared_sm07_state_ensemble):
    se = prepared_sm07_state_ensemble
    
    # calculated from Uni-pKa
    # Uni-pka model specific variable for pH dependent deltaG
    # Training might be conducted with a dataset in which raw pKa values
    # were subtracted by the mean value (TRANSLATE_PH).
    dG = np.array([
        -6.025253772735596, 
        -2.9201512336730957, 
        -2.7405877113342285, 
          -2.9639060497283936, 
          7.656927108764648, 
          19.67357063293457, 
          21.269811630249023, 
          11.911577224731445, 
          7.5623698234558105, 
          10.144123077392578, 
          21.36874008178711, 
          12.132856369018555])

    se.set_energies(dG, ref_ph=6.504894871171601)
    ph_values = np.linspace(-5, 20, 250)
    p = se.get_population(ph_values, C=math.log(10), beta=1.0)

    charge_groups_per_site = se.get_charge_groups_per_site()
    assert charge_groups_per_site == {
        5: {0: [0, 2, 3, 7], 1: [1, 5, 6, 10], -1: [4, 8, 9, 11]}, 
        7: {0: [0, 1, 3, 4, 6, 9], 1: [2, 5, 7, 8, 10, 11]}, 
        9: {0: [0, 1, 2, 4, 5, 8], 1: [3, 6, 7, 9, 10, 11]}}
    
    micropka = se.get_micro_pKa(ph_values, p)
    print(micropka)
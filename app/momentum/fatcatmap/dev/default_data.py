from google.appengine.ext import db


def add_services():

    from momentum.fatcatmap.models.services import ExtService
    from momentum.fatcatmap.models.services import ExtServiceKey

    sunlight = ExtService(key_name='sunlight')
    sunlight.name = 'Sunlight Labs'
    sunlight.description = 'Non-profit providing data about legislators, committees and committee memberships, and districts.'
    sunlight.homepage = 'http://sunlightlabs.com'
    sunlight.put()

    opensecrets = ExtService(key_name='opensecrets')
    opensecrets.name = 'CRP OpenSecrets'
    opensecrets.description = 'Non-profit providing data about contributions, lobbying, and spending.'
    opensecrets.homepage = 'http://opensecrets.org'
    opensecrets.put()

    models = []
    models.append(ExtServiceKey(sunlight, key_name='s@providenceclarity.com', name='s@providenceclarity.com', value='5716fd8eb1ce418095fe402c7489281e', enforce_limits=False))
    models.append(ExtServiceKey(opensecrets, key_name='s@providenceclarity.com', name='s@providenceclarity.com', value='254615061689494a6ef579d65d08fb70', enforce_limits=False))

    return db.put(models)+[sunlight, opensecrets]


def add_political_parties():

    from momentum.fatcatmap.models.politics import PoliticalParty

    models = []
    models.append(PoliticalParty(key_name='D', name='Democratic Party', plural='Democrats', singular='Democrat'))
    models.append(PoliticalParty(key_name='R', name='Republican Party', plural='Republicans', singular='Republican'))
    models.append(PoliticalParty(key_name='I', name='Independent Party', plural='Independents', singular='Independent'))

    return db.put(models)


def add_federal_legislature():

    from momentum.fatcatmap.models.politics import Legislature
    from momentum.fatcatmap.models.politics import LowerLegislativeHouse
    from momentum.fatcatmap.models.politics import UpperLegislativeHouse

    models = []
    congress = Legislature(key_name='us_congress',name='United States Congress', short_name='Congress', total_members=535).put()
    models.append(LowerLegislativeHouse(congress, legislature=congress, title_abbr='Rep', key_name='lower_house', name='United States House of Representatives', short_name='House of Representatives', total_members=435))
    models.append(LowerLegislativeHouse(congress, legislature=congress, title_abbr='Sen', key_name='upper_house', name='United States Senate', short_name='Senate', total_members=100))

    return db.put(models)+[congress]


def add_states():

    from momentum.fatcatmap.models.geo import USState

    models = []
    models.append(USState(key_name="AL",abbreviation="AL",fullname="Alabama",primary_display_text="Alabama",display_text=["AL","Alabama"]))
    models.append(USState(key_name="AK",abbreviation="AK",fullname="Alaska",primary_display_text="Alaska",display_text=["AK","Alaska"]))
    models.append(USState(key_name="AZ",abbreviation="AZ",fullname="Arizona",primary_display_text="Arizona",display_text=["AZ","Arizona"]))
    models.append(USState(key_name="AR",abbreviation="AR",fullname="Arkansas",primary_display_text="Arkansas",display_text=["AR","Arkansas"]))
    models.append(USState(key_name="CA",abbreviation="CA",fullname="California",primary_display_text="California",display_text=["CA","California"]))
    models.append(USState(key_name="CO",abbreviation="CO",fullname="Colorado",primary_display_text="Colorado",display_text=["CO","Colorado"]))
    models.append(USState(key_name="CT",abbreviation="CT",fullname="Connecticut",primary_display_text="Connecticut",display_text=["CT","Connecticut"]))
    models.append(USState(key_name="DE",abbreviation="DE",fullname="Delaware",primary_display_text="Delaware",display_text=["DE","Delaware"]))
    models.append(USState(key_name="FL",abbreviation="FL",fullname="Florida",primary_display_text="Florida",display_text=["FL","Florida"]))
    models.append(USState(key_name="GA",abbreviation="GA",fullname="Georgia",primary_display_text="Georgia",display_text=["GA","Georgia"]))
    models.append(USState(key_name="HI",abbreviation="HI",fullname="Hawaii",primary_display_text="Hawaii",display_text=["HI","Hawaii"]))
    models.append(USState(key_name="ID",abbreviation="ID",fullname="Idaho",primary_display_text="Idaho",display_text=["ID","Idaho"]))
    models.append(USState(key_name="IL",abbreviation="IL",fullname="Illinois",primary_display_text="Illinois",display_text=["IL","Illinois"]))
    models.append(USState(key_name="IN",abbreviation="IN",fullname="Indiana",primary_display_text="Indiana",display_text=["IN","Indiana"]))
    models.append(USState(key_name="IA",abbreviation="IA",fullname="Iowa",primary_display_text="Iowa",display_text=["IA","Iowa"]))
    models.append(USState(key_name="KS",abbreviation="KS",fullname="Kansas",primary_display_text="Kansas",display_text=["KS","Kansas"]))
    models.append(USState(key_name="KY",abbreviation="KY",fullname="Kentucky",primary_display_text="Kentucky",display_text=["KY","Kentucky"]))
    models.append(USState(key_name="LA",abbreviation="LA",fullname="Louisiana",primary_display_text="Louisiana",display_text=["LA","Louisiana"]))
    models.append(USState(key_name="ME",abbreviation="ME",fullname="Maine",primary_display_text="Maine",display_text=["ME","Maine"]))
    models.append(USState(key_name="MD",abbreviation="MD",fullname="Maryland",primary_display_text="Maryland",display_text=["MD","Maryland"]))
    models.append(USState(key_name="MA",abbreviation="MA",fullname="Massachusetts",primary_display_text="Massachusetts",display_text=["MA","Massachusetts"]))
    models.append(USState(key_name="MI",abbreviation="MI",fullname="Michigan",primary_display_text="Michigan",display_text=["MI","Michigan"]))
    models.append(USState(key_name="MN",abbreviation="MN",fullname="Minnesota",primary_display_text="Minnesota",display_text=["MN","Minnesota"]))
    models.append(USState(key_name="MS",abbreviation="MS",fullname="Mississippi",primary_display_text="Mississippi",display_text=["MS","Mississippi"]))
    models.append(USState(key_name="MO",abbreviation="MO",fullname="Missouri",primary_display_text="Missouri",display_text=["MO","Missouri"]))
    models.append(USState(key_name="MT",abbreviation="MT",fullname="Montana",primary_display_text="Montana",display_text=["MT","Montana"]))
    models.append(USState(key_name="NE",abbreviation="NE",fullname="Nebraska",primary_display_text="Nebraska",display_text=["NE","Nebraska"]))
    models.append(USState(key_name="NV",abbreviation="NV",fullname="Nevada",primary_display_text="Nevada",display_text=["NV","Nevada"]))
    models.append(USState(key_name="NH",abbreviation="NH",fullname="New Hampshire",primary_display_text="New Hampshire",display_text=["NH","New Hampshire"]))
    models.append(USState(key_name="NJ",abbreviation="NJ",fullname="New Jersey",primary_display_text="New Jersey",display_text=["NJ","New Jersey"]))
    models.append(USState(key_name="NM",abbreviation="NM",fullname="New Mexico",primary_display_text="New Mexico",display_text=["NM","New Mexico"]))
    models.append(USState(key_name="NY",abbreviation="NY",fullname="New York",primary_display_text="New York",display_text=["NY","New York"]))
    models.append(USState(key_name="NC",abbreviation="NC",fullname="North Carolina",primary_display_text="North Carolina",display_text=["NC","North Carolina"]))
    models.append(USState(key_name="ND",abbreviation="ND",fullname="North Dakota",primary_display_text="North Dakota",display_text=["ND","North Dakota"]))
    models.append(USState(key_name="OH",abbreviation="OH",fullname="Ohio",primary_display_text="Ohio",display_text=["OH","Ohio"]))
    models.append(USState(key_name="OK",abbreviation="OK",fullname="Oklahoma",primary_display_text="Oklahoma",display_text=["OK","Oklahoma"]))
    models.append(USState(key_name="OR",abbreviation="OR",fullname="Oregon",primary_display_text="Oregon",display_text=["OR","Oregon"]))
    models.append(USState(key_name="PA",abbreviation="PA",fullname="Pennsylvania",primary_display_text="Pennsylvania",display_text=["PA","Pennsylvania"]))
    models.append(USState(key_name="RI",abbreviation="RI",fullname="Rhode Island",primary_display_text="Rhode Island",display_text=["RI","Rhode Island"]))
    models.append(USState(key_name="SC",abbreviation="SC",fullname="South Carolina",primary_display_text="South Carolina",display_text=["SC","South Carolina"]))
    models.append(USState(key_name="SD",abbreviation="SD",fullname="South Dakota",primary_display_text="South Dakota",display_text=["SD","South Dakota"]))
    models.append(USState(key_name="TN",abbreviation="TN",fullname="Tennessee",primary_display_text="Tennessee",display_text=["TN","Tennessee"]))
    models.append(USState(key_name="TX",abbreviation="TX",fullname="Texas",primary_display_text="Texas",display_text=["TX","Texas"]))
    models.append(USState(key_name="UT",abbreviation="UT",fullname="Utah",primary_display_text="Utah",display_text=["UT","Utah"]))
    models.append(USState(key_name="VT",abbreviation="VT",fullname="Vermont",primary_display_text="Vermont",display_text=["VT","Vermont"]))
    models.append(USState(key_name="VA",abbreviation="VA",fullname="Virginia",primary_display_text="Virginia",display_text=["VA","Virginia"]))
    models.append(USState(key_name="WA",abbreviation="WA",fullname="Washington",primary_display_text="Washington",display_text=["WA","Washington"]))
    models.append(USState(key_name="WV",abbreviation="WV",fullname="West Virginia",primary_display_text="West Virginia",display_text=["WV","West Virginia"]))
    models.append(USState(key_name="WI",abbreviation="WI",fullname="Wisconsin",primary_display_text="Wisconsin",display_text=["WI","Wisconsin"]))
    models.append(USState(key_name="WY",abbreviation="WY",fullname="Wyoming",primary_display_text="Wyoming",display_text=["WY","Wyoming"]))

    return db.put(models)



all_functions = [add_services, add_political_parties, add_federal_legislature, add_states]
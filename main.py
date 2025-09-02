from beamngpy import BeamNGpy, Scenario, Vehicle

BEAMNGTECHDIR = "C:\\Users\\David Gillig\\Downloads\\BeamNG.tech.v0.36.4.0"

bng = BeamNGpy('localhost', 25252, home=BEAMNGTECHDIR)
bng.open(None, '-gfx', 'vk')

scenario = Scenario('east_coast_usa', 'test1')
main_vehicle = Vehicle('main_vehicle', model='etk800', license='TEST')
scenario.add_vehicle(main_vehicle, pos=(-772,476,24), cling=True)
scenario.make(bng)

bng.scenario.load(scenario)
bng.traffic.spawn(10)

bng.scenario.start()

#main_vehicle.ai.set_mode('traffic')
input('Enter to finish')

bng.close()
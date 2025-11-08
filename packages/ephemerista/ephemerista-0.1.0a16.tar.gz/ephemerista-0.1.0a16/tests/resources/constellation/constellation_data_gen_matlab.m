function constellation_to_json(nsats, nplanes, phasing, semi_major_axis, inclination, eccentricity, periapsis_argument, epoch, constel_name, constellation_type)
    sc = satelliteScenario;
    
    if constellation_type == "walker_star"
        constellation = walkerStar(sc, semi_major_axis*1e3, inclination, nsats, nplanes, phasing, Name=constel_name);
    elseif constellation_type == "walker_delta"
        constellation = walkerDelta(sc, semi_major_axis*1e3, inclination, nsats, nplanes, phasing, Name=constel_name);
    end
    
    constel.nsats = uint16(nsats);
    constel.nplanes = uint16(nplanes);
    constel.semi_major_axis = semi_major_axis;
    constel.inclination = inclination;
    constel.eccentricity = eccentricity;
    constel.periapsis_argument = periapsis_argument;
    constel.name = constel_name;

    origin.body_type = "planet";
    origin.name = "Earth";
    constel.origin = origin;

    timestamp.time_type = 'iso';
    timestamp.value = epoch;
    time.timestamp = timestamp;
    time.scale = 'TDB';
    constel.time = time;

    constel.constellation_type = constellation_type;

    for i = 1:constel.nsats
        sat_i = constellation(i);
        clear sma_shape sat_json inc node arg anomaly
        sat_json.time = time;
        sat_json.origin = origin;
        sat_json.state_type = 'keplerian';
        
        elements = orbitalElements(sat_i);
    
        sma_shape.shape_type = 'semi_major';
        sma_shape.sma = 1e-3 * elements.SemiMajorAxis;
        sma_shape.ecc = elements.Eccentricity;
        sat_json.shape = sma_shape;
        
        inc.degrees = elements.Inclination;
        sat_json.inc = inc;
    
        node.degrees = elements.RightAscensionOfAscendingNode;
        sat_json.node = node;
    
        arg.degrees = elements.ArgumentOfPeriapsis;
        sat_json.arg = arg;
    
        anomaly.degrees = elements.TrueAnomaly;
        if anomaly.degrees > 180
            anomaly.degrees = anomaly.degrees - 360;
        end
        anomaly.anomaly_type = 'true_anomaly';
        sat_json.anomaly = anomaly;
    
        satellites(i) = sat_json;
    end

    constel.satellites = satellites;
    
    writestruct(constel, append(constel_name, '_', constellation_type, "_matlab.json"), PrettyPrint=true);

end

function walker_star_1
    sc = satelliteScenario;
    
    nsats = 64;
    nplanes = 8;
    phasing = 2;
    semi_major_axis = 7000.0;
    inclination = 45.0;
    eccentricity = 0.0;
    periapsis_argument = 0.0;
    epoch = '2016-05-30T12:00:00';
    constel_name = 'constellation1';
    constellation_type = 'walker_star';
    
    constellation_to_json(nsats, nplanes, phasing, ...
        semi_major_axis, inclination, eccentricity, ...
        periapsis_argument, epoch, constel_name, constellation_type);
end

function walker_star_oneweb
    sc = satelliteScenario;
    
    nsats = 648;
    nplanes = 18;
    phasing = 0;
    semi_major_axis = 7578.0;
    inclination = 86.4;
    eccentricity = 0.0;
    periapsis_argument = 0.0;
    epoch = '2016-05-30T12:00:00';
    constel_name = 'oneweb';
    constellation_type = 'walker_star';
    
    constellation_to_json(nsats, nplanes, phasing, ...
        semi_major_axis, inclination, eccentricity, ...
        periapsis_argument, epoch, constel_name, constellation_type);
end

function walker_delta_1
    sc = satelliteScenario;
    
    nsats = 72;
    nplanes = 9;
    phasing = 4;
    semi_major_axis = 7000.0;
    inclination = 98.0;
    eccentricity = 0.0;
    periapsis_argument = 0.0;
    epoch = '2016-05-30T12:00:00';
    constel_name = 'constellation2';
    constellation_type = 'walker_delta';
    
    constellation_to_json(nsats, nplanes, phasing, ...
        semi_major_axis, inclination, eccentricity, ...
        periapsis_argument, epoch, constel_name, constellation_type);
end

function walker_delta_galileo
    sc = satelliteScenario;
    
    nsats = 24;
    nplanes = 3;
    phasing = 1;
    semi_major_axis = 29599.8;
    inclination = 56.0;
    eccentricity = 0.0;
    periapsis_argument = 0.0;
    epoch = '2016-05-30T12:00:00';
    constel_name = 'galileo';
    constellation_type = 'walker_delta';
    
    constellation_to_json(nsats, nplanes, phasing, ...
        semi_major_axis, inclination, eccentricity, ...
        periapsis_argument, epoch, constel_name, constellation_type);
end

walker_star_1;
walker_star_oneweb;
walker_delta_1;
walker_delta_galileo;
%% Define dipole antenna, with default dimensions in MATLAB chosen for an operating frequency of around 70 MHz.
ant = dipoleCylindrical();

%% Write antenna pattern at 70 MHz to MSI file
f = 70e6;
msiwrite(ant, f, "cylindricalDipole", Name="Cylindrical dipole from MATLAB (default parameters)");

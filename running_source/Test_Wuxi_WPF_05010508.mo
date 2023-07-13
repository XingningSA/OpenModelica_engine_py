within HVAC.AirSideSystem.Tests;

model Test_Wuxi_WPF_05010508
  RoomWithFCU roomWithFCU(CWallPerArea = 457385, EnableWatPort = false, FCU_nominal_UA = 19000, FCU_nominal_air_m(displayUnit = "kg/s") = 150, FCU_nominal_wat_m(displayUnit = "kg/s") = 150, GWin = 0.691, HorizontalLength = 119.87, InitRH = 0.785, InitTDryBulb = 291.89, IsHeating = false, KpTi = {0.5, 300}, Lat = 0.5496245843519701, LeftFaceOutside = true, LeftSurfaceWWR = 0.03788, Lon = 2.099838958863091, LowerFaceOutside = true, LowerSurfaceWWR = 0.0794, RightFaceOutside = true, RightSurfaceWWR = 0.020266, RoomHeight = 18.3, TimeZone = 8*3600, UWall = 1, UWin = 3.4, UpperAzi(displayUnit = "rad") = -0.69813, UpperFaceOutside = true, UpperSurfaceWWR = 0.06467, UsePIControl = true, VerticalLength = 78.3) annotation(
    Placement(transformation(extent = {{-18, -50}, {78, 42}})));
  Modelica.Blocks.Sources.Constant equipGain(k = 190000) annotation(
    Placement(visible = true, transformation(origin = {-80, -56}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant FCU_AirFlowRatio(k = 1) annotation(
    Placement(visible = true, transformation(origin = {-26, 84}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Sources.CombiTimeTable OARH(columns = 1:2, fileName = "D:/Fuzor2020/simulation-WuxiWPF/OARHfull.txt", tableName = "OARHwuxi", tableOnFile = true) annotation(
    Placement(visible = true, transformation(origin = {-88, 52}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.CombiTimeTable SolDNI(columns = 1:2, fileName = "D:/Fuzor2020/simulation-WuxiWPF/DNIfull.txt", tableName = "DNIwuxi", tableOnFile = true) annotation(
    Placement(visible = true, transformation(origin = {-148, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.CombiTimeTable SolDHI(columns = 1:2, fileName = "D:/Fuzor2020/simulation-WuxiWPF/DHIfull.txt", tableName = "DHIwuxi", tableOnFile = true) annotation(
    Placement(visible = true, transformation(origin = {-112, -12}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.CombiTimeTable OAT(columns = 1:2, fileName = "D:/Fuzor2020/simulation-WuxiWPF/OATfull.txt", tableName = "OATwuxi", tableOnFile = true) annotation(
    Placement(visible = true, transformation(origin = {-66, 80}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant const(k = 0.7) annotation(
    Placement(visible = true, transformation(origin = {-62, -84}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.CombiTimeTable CC(columns = 1:2, fileName = "D:/Fuzor2020/simulation-WuxiWPF/CCfull.txt", tableName = "CCwuxi", tableOnFile = true) annotation(
    Placement(visible = true, transformation(origin = {-124, 34}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.CombiTimeTable Setpoint(columns = 1:2, fileName = "D:/Fuzor2020/simulation-WuxiWPF/STfull.txt", tableName = "STwuxi", tableOnFile = true)  annotation(
    Placement(visible = true, transformation(origin = {-8, 110}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant constant1(k = 65) annotation(
    Placement(visible = true, transformation(origin = {-114, -44}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Sources.CombiTimeTable WaterIn(columns = 1:2, fileName = "D:/Fuzor2020/simulation-WuxiWPF/WaterIn.txt", tableName = "WATERwuxi", tableOnFile = true)  annotation(
    Placement(visible = true, transformation(origin = {26, 102}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Product product annotation(
    Placement(visible = true, transformation(origin = {130, -56}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Add add(k1 = -1)  annotation(
    Placement(visible = true, transformation(origin = {122, 50}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant constant2(k = 4.1868) annotation(
    Placement(visible = true, transformation(origin = {118, 14}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Math.Product coolingload annotation(
    Placement(visible = true, transformation(origin = {206, -6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  connect(roomWithFCU.EquipGain, equipGain.y) annotation(
    Line(points = {{-21.6, -22.17}, {-64, -22.17}, {-64, -56}, {-73.4, -56}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(FCU_AirFlowRatio.y, roomWithFCU.FCU_airflow_ratio) annotation(
    Line(points = {{-19.4, 84}, {-8.4, 84}, {-8.4, 45.68}}, color = {0, 0, 127}));
  connect(OAT.y[2], roomWithFCU.OAT) annotation(
    Line(points = {{-54, 80}, {-40, 80}, {-40, 42}, {-22, 42}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(SolDNI.y[2], roomWithFCU.SolDirNorm) annotation(
    Line(points = {{-137, 10}, {-64.5, 10}, {-64.5, 14}, {-22, 14}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(SolDHI.y[2], roomWithFCU.SolDifHori) annotation(
    Line(points = {{-100, -12}, {-76, -12}, {-76, 6}, {-22, 6}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(const.y, roomWithFCU.InputInfiltration) annotation(
    Line(points = {{-51, -84}, {-36, -84}, {-36, -32}, {-22, -32}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(CC.y[2], roomWithFCU.SkyCoverTenths) annotation(
    Line(points = {{-112, 34}, {-80, 34}, {-80, 24}, {-22, 24}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(Setpoint.y[2], roomWithFCU.IAT_SP) annotation(
    Line(points = {{4, 110}, {10, 110}, {10, 46}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(constant1.y, roomWithFCU.nPeople) annotation(
    Line(points = {{-108, -44}, {-72, -44}, {-72, -12}, {-22, -12}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(WaterIn.y[2], roomWithFCU.WatTIn) annotation(
    Line(points = {{38, 102}, {40, 102}, {40, 64}, {20, 64}, {20, 46}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(roomWithFCU.FCU_WatMassFlow, product.u1) annotation(
    Line(points = {{82, -26}, {118, -26}, {118, -50}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(WaterIn.y[2], add.u1) annotation(
    Line(points = {{38, 102}, {78, 102}, {78, 56}, {110, 56}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(roomWithFCU.FCU_WatTOut, add.u2) annotation(
    Line(points = {{82, -36}, {152, -36}, {152, 30}, {100, 30}, {100, 44}, {110, 44}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(add.y, product.u2) annotation(
    Line(points = {{134, 50}, {134, -9}, {118, -9}, {118, -62}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(constant2.y, coolingload.u1) annotation(
    Line(points = {{125, 14}, {163, 14}, {163, 0}, {194, 0}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(product.y, coolingload.u2) annotation(
    Line(points = {{141, -56}, {158, -56}, {158, -12}, {194, -12}}, color = {0, 0, 127}, pattern = LinePattern.Solid));
  connect(OARH.y[2], roomWithFCU.OARH) annotation(
    Line(points = {{-76, 52}, {-58, 52}, {-58, 34}, {-22, 34}}, color = {0, 0, 127}));
  annotation(
    Icon(coordinateSystem(preserveAspectRatio = false, extent = {{-100, -100}, {100, 100}}), graphics = {Rectangle(fillColor = {0, 85, 255}, fillPattern = FillPattern.Solid, lineThickness = 1, extent = {{-100, 102}, {104, -98}}), Rectangle(origin = {3, 1}, fillColor = {0, 170, 0}, fillPattern = FillPattern.Solid, extent = {{-81, 81}, {81, -81}}), Text(origin = {5, 9}, textColor = {255, 255, 255}, extent = {{-81, 59}, {81, -59}}, textString = "t", textStyle = {TextStyle.Bold})}),
    Diagram(coordinateSystem(preserveAspectRatio = false)));

end Test_Wuxi_WPF_05010508;

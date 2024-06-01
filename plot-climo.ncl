load "./ncl_utils/shapefile_utils.ncl"

begin

models = (/"L15","NLDAS","JRA","E3SM"/)

use_max_for_plotting=False

if (isvar("auto_domain_climo") .and. str_lower(auto_domain_climo) .eq. "true") then
  get_plot_domain_from_f1=True
else
  get_plot_domain_from_f1=False
end if
print("get_plot_domain_from_f1: "+get_plot_domain_from_f1)

f1 = addfile("./netcdf/"+models(0)+"_1985to2005_masked.nc","r")
f2 = addfile("./netcdf/"+models(1)+"_1985to2005_masked.nc","r")
f3 = addfile("./netcdf/"+models(2)+"_1985to2005_masked.nc","r")
f4 = addfile("./netcdf/"+models(3)+"_1985to2005_masked.nc","r")

shpfilename="./shapes/"+basinshape+"/"+basinshape+".shp"
shp = addfile(shpfilename,"r")

; settings
;var="ROF"
winter_only=True

; print units next to colorbar?
colorbar_units=True

;debugging
check_L15=False
check_NLDAS=False
only_obs=False

rof1 = f1->$var$
rof2 = f2->$var$
if (only_obs) then
  rof3 = rof1
  rof3 = 0.0
  rof4 = rof3
else
  rof3 = f3->$var$
  rof4 = f4->$var$
end if

rof1_time = cd_calendar(f1->time,0)
rof1_month = rof1_time(:,1)
rof1_2D = conform_dims(dimsizes(rof1),rof1_month,0)

rof2_time = cd_calendar(f1->time,0)
rof2_month = rof2_time(:,1)
rof2_2D = conform_dims(dimsizes(rof2),rof2_month,0)

rof3_time = cd_calendar(f1->time,0)
rof3_month = rof3_time(:,1)
rof3_2D = conform_dims(dimsizes(rof3),rof3_month,0)

rof4_time = cd_calendar(f1->time,0)
rof4_month = rof4_time(:,1)
rof4_2D = conform_dims(dimsizes(rof4),rof4_month,0)

if ((check_L15 .or. check_NLDAS) .and. winter_only) then
  print("Cannot have a check on and only winter, resetting winter_only to False")
  winter_only = False
end if
if (check_L15 .and. check_NLDAS) then
  print("both check L15 and check NLDAS cannot be on")
  exit
end if
if (winter_only) then
  rof1 = where(rof1_2D.lt.11 .and. rof1_2D.gt.4,rof1@_FillValue,rof1)
  rof2 = where(rof2_2D.lt.11 .and. rof2_2D.gt.4,rof2@_FillValue,rof2)
  rof3 = where(rof3_2D.lt.11 .and. rof3_2D.gt.4,rof3@_FillValue,rof3)
  rof4 = where(rof4_2D.lt.11 .and. rof4_2D.gt.4,rof4@_FillValue,rof4)
end if

;if (var .eq. "dSWE") then
;  rof1=abs(rof1)
;;  rof2=abs(rof2)
;  rof3=abs(rof3)
;  rof4=abs(rof4)
;end if
; if dSWE, set all 0 and positive values to nans
if (var .eq. "dSWE") then
  rof1=where(rof1 .lt. 0.000,rof1,rof1@_FillValue)
  rof2=where(rof2 .lt. 0.000,rof2,rof2@_FillValue)
  rof3=where(rof3 .lt. 0.000,rof3,rof3@_FillValue)
  rof4=where(rof4 .lt. 0.000,rof4,rof4@_FillValue)
end if

if (check_L15) then
  shortlat := tofloat(rof1&lat)
  shortlon := tofloat(rof1&lon)
  shortlon := shortlon + 360.

  delete(f4)
  delete(rof4)
  if (var .eq. "ROF") then
    f4 = addfile("./netcdf/q.mon.ltm.nc","r")
    rof4 = f4->q(:,{shortlat},{shortlon})
    rof4 = rof4*86400.
    ; NOTE: CMZ tested surface + baseflow 3/23 and found this overshoots
    ; sfc runoff from other data, so don't think this is source of low L15 ROF
    ;t4 = addfile("./netcdf/qsb.mon.ltm.nc","r")
    ;tof4 = t4->qsb(:,{shortlat},{shortlon})
    ;tof4 = tof4*86400.
    ;rof4 = rof4 + tof4
  else if (var .eq. "SWE") then
    f4 = addfile("./netcdf/swe.mon.ltm.nc","r")
    rof4 = f4->swe(:,{shortlat},{shortlon})
  else
    print("trying to check var that isn't supported")
    exit
  end if
  end if

  models(3) = "L15 LTM"
end if

if (check_NLDAS) then
  shortlat := rof2&lat
  shortlon := rof2&lon

  delete(f1)
  delete(rof1)
  filelist = systemfunc("ls /Users/cmz5202/Software/ros/ALL_PY/NLDAS2-Verif/NLDAS_VIC0125_MC*.nc")
  print(filelist)
  f1 = addfiles(filelist,"r")
  ListSetType (f1, "join")
  if (var .eq. "ROF") then
    rof1 = f1[:]->SSRUN_110_SFC_S51(:,{shortlat},{shortlon})
    rof1 = rof1 / 30.
  else if (var .eq. "SWE") then
    rof1 = f1[:]->WEASD_110_SFC_S51(:,{shortlat},{shortlon})
  else
    print("trying to check var that isn't supported")
    exit
  end if
  end if
  rof1!2="lon"
  rof1&lat=f1[0]->lat_110({shortlat})
  rof1&lon=f1[0]->lon_110({shortlon})
  printVarSummary(rof1)

  delete(f3)
  delete(rof3)
  if (var .eq. "ROF") then
    f3 = addfile("/Users/cmz5202/Software/ros/ALL_PY/NLDAS2-Verif/SSRUN_GDS0_SFC_acc1h_VIC_avg.nc","r")
    rof3 = f3->SSRUN_GDS0_SFC_acc1h(:,{shortlat},{shortlon})
    rof3 = rof3 * 24.
  else if (var .eq. "SWE") then
    f3 = addfile("/Users/cmz5202/Software/ros/ALL_PY/NLDAS2-Verif/WEASD_GDS0_SFC_VIC_avg.nc","r")
    rof3 = f3->WEASD_GDS0_SFC(:,{shortlat},{shortlon})
  else
    print("trying to check var that isn't supported")
    exit
  end if
  end if
  rof3!1="lat"
  rof3!2="lon"
  rof3&lat=f3->g0_lat_0({shortlat})
  rof3&lon=f3->g0_lon_1({shortlon})

  models(0) = "NLDAS2"
  models(2) = "NLDAS4.0.5_avg"
end if

rof1&lat@units="degrees_north"
rof1&lon@units="degrees_east"
rof1@_FillValue=-999.9
rof1 = where(isnan_ieee(rof1),rof1@_FillValue,rof1)

rof2&lat@units="degrees_north"
rof2&lon@units="degrees_east"
rof2@_FillValue=-999.9
rof2 = where(isnan_ieee(rof2),rof2@_FillValue,rof2)

rof3&lat@units="degrees_north"
rof3&lon@units="degrees_east"
rof3@_FillValue=-999.9
rof3 = where(isnan_ieee(rof3),rof3@_FillValue,rof3)

rof4&lat@units="degrees_north"
rof4&lon@units="degrees_east"
rof4@_FillValue=-999.9
rof4 = where(isnan_ieee(rof4),rof4@_FillValue,rof4)

rof1_avg = dim_avg_n_Wrap(rof1,0)
rof2_avg = dim_avg_n_Wrap(rof2,0)
rof3_avg = dim_avg_n_Wrap(rof3,0)
rof4_avg = dim_avg_n_Wrap(rof4,0)

if (check_NLDAS) then
  rof1_avg = where(ismissing(rof2_avg),rof1_avg@_FillValue,rof1_avg)
  rof3_avg = where(ismissing(rof2_avg),rof3_avg@_FillValue,rof3_avg)
end if
if (check_L15) then
  rof4_avg = where(ismissing(rof1_avg),rof4_avg@_FillValue,rof4_avg)
end if

rad    = 4.0*atan(1.0)/180.0
rof1_avg_avg = wgt_areaave_Wrap(rof1_avg, cos(rof1_avg&lat*rad), 1.0, 1)
rof2_avg_avg = wgt_areaave_Wrap(rof2_avg, cos(rof2_avg&lat*rad), 1.0, 1)
rof3_avg_avg = wgt_areaave_Wrap(rof3_avg, cos(rof3_avg&lat*rad), 1.0, 1)
rof4_avg_avg = wgt_areaave_Wrap(rof4_avg, cos(rof4_avg&lat*rad), 1.0, 1)

print("min: "+min(rof1_avg)+"   max: "+max(rof1_avg)+"     mean: "+avg(rof1_avg)+"     wgt_avg: "+rof1_avg_avg)
print("min: "+min(rof2_avg)+"   max: "+max(rof2_avg)+"     mean: "+avg(rof2_avg)+"     wgt_avg: "+rof2_avg_avg)
print("min: "+min(rof3_avg)+"   max: "+max(rof3_avg)+"     mean: "+avg(rof3_avg)+"     wgt_avg: "+rof3_avg_avg)
print("min: "+min(rof4_avg)+"   max: "+max(rof4_avg)+"     mean: "+avg(rof4_avg)+"     wgt_avg: "+rof4_avg_avg)

if (var .eq. "dSWE") then
  max_for_plotting = min(rof1_avg)
  max_for_plotting = min((/min(rof2_avg),max_for_plotting/))
  max_for_plotting = min((/min(rof3_avg),max_for_plotting/))
  max_for_plotting = min((/min(rof4_avg),max_for_plotting/))
  print("min for plotting: "+max_for_plotting)
else
  max_for_plotting = max(rof1_avg)
  max_for_plotting = max((/max(rof2_avg),max_for_plotting/))
  max_for_plotting = max((/max(rof3_avg),max_for_plotting/))
  max_for_plotting = max((/max(rof4_avg),max_for_plotting/))
  print("max for plotting: "+max_for_plotting)
end if

output_directory="./output/"+basinshape+"/climo"
system("mkdir -p "+output_directory)

wks = gsn_open_wks("pdf",output_directory+"/climo_comp_panel_"+var)              ; send graphics to PNG file

plot = new(4,graphic)                          ; create a plot array

res                     = True
res@gsnDraw             = False           ; don't draw
res@gsnFrame            = False           ; don't advance frame
res@cnInfoLabelOn       = False           ; turn off cn info label
res@cnFillOn            = True            ; turn on color
res@lbLabelBarOn        = False           ; turn off individual cb's
res@gsnAddCyclic = False
res@cnFillMode = "RasterFill"
res@cnLinesOn = False
res@cnLineLabelsOn  = False

if (var .eq. "ROF")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = 0.05
  if (use_max_for_plotting) then
    res@cnMaxLevelValF       = max_for_plotting
  else
    res@cnMaxLevelValF       = 0.8
  end if
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/15.0
  cmap                     := read_colormap_file("MPL_BuGn")
  res@cnFillPalette        := cmap
end if
if (var .eq. "BASE")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = 0.05
  res@cnMaxLevelValF       = 1.55
  res@cnLevelSpacingF      = 0.10
  cmap                     := read_colormap_file("MPL_BuGn")
  res@cnFillPalette        := cmap
end if
if (var .eq. "ET")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = 0.2
  res@cnMaxLevelValF       = 2.4
  res@cnLevelSpacingF      = 0.2
  cmap                     := read_colormap_file("MPL_BuGn")
  res@cnFillPalette        := cmap
end if
if (var .eq. "PRECIP")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = 2.1
  if (use_max_for_plotting) then
    res@cnMaxLevelValF       = max_for_plotting
  else
    res@cnMaxLevelValF       = 3.8
  end if
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/17.0
  cmap                     := read_colormap_file("cmocean_matter")
  res@cnFillPalette        := cmap
end if
if (var .eq. "SWE")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = 0.
  max_scaling = 0.5
  if (use_max_for_plotting) then
    res@cnMaxLevelValF       = max_for_plotting * max_scaling
  else
    res@cnMaxLevelValF       = 40.0
  end if
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/40.0
  cmap                     := read_colormap_file("cmocean_dense")
  res@cnFillPalette        := cmap
end if
if (var .eq. "dSWE")
  res@cnLevelSelectionMode =  "ManualLevels"
  if (use_max_for_plotting) then
    res@cnMinLevelValF       = max_for_plotting
  else
    res@cnMinLevelValF       = -4.0
  end if
  res@cnMaxLevelValF       =  -1.2
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/28.0
  cmap                     := read_colormap_file("MPL_YlGnBu")
  res@cnFillPalette        := cmap(::-1,:)
end if

if (get_plot_domain_from_f1) then
  res@mpMaxLatF=max(f1->lat)
  res@mpMinLatF=min(f1->lat)
  res@mpMinLonF=min(f1->lon)
  res@mpMaxLonF=max(f1->lon)
else
  res@mpMaxLatF=43.1
  res@mpMinLatF=39.3
  res@mpMinLonF=280.7
  res@mpMaxLonF=285.7
end if
res@mpCenterLonF=(res@mpMinLonF+res@mpMaxLonF)/2.

res@mpDataBaseVersion = "MediumRes"
res@mpOutlineBoundarySets = "USStates"
res@mpOutlineDrawOrder = "PostDraw"

res@gsnMajorLatSpacing = 1.0
res@gsnMajorLonSpacing = 2.0

tickLength=0.001
res@tmXTMajorLengthF     = tickLength
res@tmXBMajorLengthF     = tickLength
res@tmYLMajorLengthF     = tickLength
res@tmYRMajorLengthF     = tickLength

tickHeight=0.018
res@tmXTLabelFontHeightF  =tickHeight
res@tmXBLabelFontHeightF  =tickHeight
res@tmYLLabelFontHeightF  =tickHeight
res@tmYRLabelFontHeightF  =tickHeight

res@gsnLeftString = var
if (var .eq. "SWE") then
  these_units="mm"
else
  these_units="mm/day"
end if

if (colorbar_units) then
  res@gsnRightString = ""
else
  res@gsnRightString = these_units
end if

res@gsnCenterString = models(0)
res@txFontHeightF=0.024

plot(0) = gsn_csm_contour_map(wks,rof1_avg,res)

res@tmYLLabelsOn  = False
res@gsnCenterString = models(1)
plot(1) = gsn_csm_contour_map(wks,rof2_avg,res)

res@gsnCenterString = models(2)
plot(2) = gsn_csm_contour_map(wks,rof3_avg,res)

res@gsnCenterString = models(3)
plot(3) = gsn_csm_contour_map(wks,rof4_avg,res)

plres = True
plres@gsLineColor = "black"
plres@gsLineThicknessF = 2.0
x = shp->x
y = shp->y

lines_id0 = gsn_add_polyline(wks,plot(0),x,y,plres)
lines_id1 = gsn_add_polyline(wks,plot(1),x,y,plres)
lines_id2 = gsn_add_polyline(wks,plot(2),x,y,plres)
lines_id3 = gsn_add_polyline(wks,plot(3),x,y,plres)

txres=True
txres@txBackgroundFillColor = "White"
txres@txFontHeightF=0.033
amres=True
amres@amParallelPosF   = 0.5    ; This is the right edge of the plot.
amres@amOrthogonalPosF = 0.5    ; This is the bottom edge of the plot.
amres@amJust           = "BottomRight"

txid0 = gsn_create_text(wks, sprintf("%4.2f", rof1_avg_avg), txres)
annoid0 = gsn_add_annotation(plot(0), txid0, amres)

txid1 = gsn_create_text(wks, sprintf("%4.2f", rof2_avg_avg), txres)
annoid1 = gsn_add_annotation(plot(1), txid1, amres)

txid2 = gsn_create_text(wks, sprintf("%4.2f", rof3_avg_avg), txres)
annoid2 = gsn_add_annotation(plot(2), txid2, amres)

txid3 = gsn_create_text(wks, sprintf("%4.2f", rof4_avg_avg), txres)
annoid3 = gsn_add_annotation(plot(3), txid3, amres)

;************************************************
; create panel
;************************************************
resP                     = True                ; modify the panel plot
;resP@gsnPanelMainString = "Climo comparison"

resP@gsnPanelLabelBar    = True
resP@lbLabelFontHeightF  = 0.012

if (colorbar_units) then
  resP@lbTitleString = these_units
  resP@lbTitlePosition  = "Right"              ; title position
  resP@lbTitleFontHeightF= .0135                ; make title smaller
  resP@lbTitleDirection = "Across"             ; title direction
  resP@lbTitleExtentF = 0.005
end if

;resP@gsnPanelXF = (/-1,0.59/)
resP@amJust = "TopLeft"
if (var .eq. "PRECIP") then
  resP@gsnPanelFigureStrings= (/"a.","b.","c.","d."/)
else if (var .eq. "ROF") then
  resP@gsnPanelFigureStrings= (/"e.","f.","g.","h."/)
else if (var .eq. "SWE") then
  resP@gsnPanelFigureStrings= (/"i.","j.","k.","l."/)
else if (var .eq. "dSWE") then
  resP@gsnPanelFigureStrings= (/"m.","n.","o.","p."/)
else
  resP@gsnPanelFigureStrings= (/"1.","2.","3.","4."/)
end if
end if
end if
end if
resP@gsnPanelFigureStringsFontHeightF  = 0.018

gsn_panel(wks,plot,(/1,4/),resP)               ; now draw as one plot



end

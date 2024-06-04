load "../ncl_utils/shapefile_utils.ncl"

begin

basinshape="srb"
model="JRA"
colorbar_units=True
var="ROF"
outtype="pdf"

f1 = addfile("../netcdf/"+model+"_1985to2005_masked_WillametteBasin.nc","r")
f2 = addfile("../netcdf/"+model+"_1985to2005_masked_SacRB_USGS1802.nc","r")

shpfilename1="../shapes/WillametteBasin/WillametteBasin.shp"
shp1 = addfile(shpfilename1,"r")

shpfilename2="../shapes/SacRB_USGS1802/SacRB_USGS1802.shp"
shp2 = addfile(shpfilename2,"r")

f1time=f1->time
time1   := cd_inv_calendar(1996,2,7,0,0,0,f1time@units, 0)
rof1 = f1->$var$({time1},:,:)

f2time=f2->time
time2   := cd_inv_calendar(1996,12,30,0,0,0,f2time@units, 0)
rof2 = f2->$var$({time2},:,:)

rof1&lat@units="degrees_north"
rof1&lon@units="degrees_east"
rof1@_FillValue=-999.9
rof1 = where(isnan_ieee(rof1),rof1@_FillValue,rof1)

rof2&lat@units="degrees_north"
rof2&lon@units="degrees_east"
rof2@_FillValue=-999.9
rof2 = where(isnan_ieee(rof2),rof2@_FillValue,rof2)

wks = gsn_open_wks(outtype,"other_basins_"+var)              ; send graphics to PNG file

plot = new(2,graphic)                          ; create a plot array

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

res@gsnMaximize=False

if (var .eq. "ROF")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = 2.0

    res@cnMaxLevelValF       = 46.0
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/22.0
  cmap                     := read_colormap_file("../ncl_utils/plasma.rgb")
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
  res@cnMaxLevelValF       = 3.8
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/17.0
  cmap                     := read_colormap_file("cmocean_matter")
  res@cnFillPalette        := cmap
end if
if (var .eq. "SWE")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = 0.
  res@cnMaxLevelValF       = 40.0
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/40.0
  cmap                     := read_colormap_file("cmocean_dense")
  res@cnFillPalette        := cmap
end if
if (var .eq. "dSWE")
  res@cnLevelSelectionMode =  "ManualLevels"
  res@cnMinLevelValF       = -4.0
  res@cnMaxLevelValF       =  -1.2
  res@cnLevelSpacingF      = (res@cnMaxLevelValF  - res@cnMinLevelValF)/28.0
  cmap                     := read_colormap_file("MPL_YlGnBu")
  res@cnFillPalette        := cmap(::-1,:)
end if



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

res@gsnLeftString=var
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

res@gsnRightString = cd_calendar(time1,-2)

res@gsnCenterString =""
res@txFontHeightF=0.024

res@tmXBLabelsOn  = True
res@tmYLLabelsOn  = True
res@mpMinLatF=41.0
res@mpMaxLatF=48.0
res@mpMinLonF=233.5
res@mpMaxLonF=240.5
res@mpCenterLonF=(res@mpMinLonF+res@mpMaxLonF)/2.
print(res@mpMinLatF+" "+res@mpMaxLatF+" "+res@mpMinLonF+" "+res@mpMaxLonF)
plot(0) = gsn_csm_contour_map(wks,rof1,res)

res@gsnRightString = cd_calendar(time2,-2)
res@tmXBLabelsOn  = True
res@tmYLLabelsOn  = True
res@gsnCenterString = ""
res@mpMinLatF=36.0
res@mpMaxLatF=44.0
res@mpMinLonF=234.5
res@mpMaxLonF=242.5
res@mpCenterLonF=(res@mpMinLonF+res@mpMaxLonF)/2.
print(res@mpMinLatF+" "+res@mpMaxLatF+" "+res@mpMinLonF+" "+res@mpMaxLonF)
plot(1) = gsn_csm_contour_map(wks,rof2,res)

plres = True
plres@gsLineColor = "black"
plres@gsLineThicknessF = 4.0

x := shp1->x
y := shp1->y
lines_id1 = gsn_add_polyline(wks,plot(0),x,y,plres)

x := shp2->x
y := shp2->y
lines_id2 = gsn_add_polyline(wks,plot(1),x,y,plres)

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

resP@amJust = "TopLeft"
resP@gsnPanelFigureStrings= (/"a.","b.","c.","d."/)
resP@gsnPanelFigureStringsFontHeightF  = 0.025

gsn_panel(wks,plot,(/1,2/),resP)               ; now draw as one plot

; pdf crop
;system("pdfcrop other_basins_"+var+"."+outtype+" other_basins_"+var+"."+outtype)

end

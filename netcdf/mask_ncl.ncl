load "../ncl_utils/shapefile_utils.ncl"

;model="NLDAS"

f = addfile(model+"_1985to2005_merged.nc","r")
shpfilename=repopath+"/shapes/srb/srb.shp"
shp = addfile(shpfilename,"r")
print_shapefile_info(shpfilename)
plot_shapefile(shpfilename)

; get SWE
SWE=f->SWE
dSWE=f->dSWE
PRECIP=f->PRECIP
ROF=f->ROF
;BASE=f->ET
;ET=f->BASE

if (min(SWE&lon) .gt. 0.0) then
  print("Need to flip lon")
  lon = SWE&lon
  newlon = lon - 360.0
  SWE&lon=newlon
end if

Opt=True
Opt@debug=True
Opt@return_mask=True

; get 2-D mask of 1s and 0s
MASK_2D = shapefile_mask_data(SWE(0,:,:),shpfilename,Opt)

MASK = conform (SWE,MASK_2D,(/1,2/))

SWE_MASK = SWE
SWE_MASK = where(MASK .gt. 0.5,SWE_MASK,SWE_MASK@_FillValue)
ROF_MASK = ROF
ROF_MASK = where(MASK .gt. 0.5,ROF_MASK,ROF_MASK@_FillValue)
PRECIP_MASK = PRECIP
PRECIP_MASK = where(MASK .gt. 0.5,PRECIP_MASK,PRECIP_MASK@_FillValue)
dSWE_MASK = dSWE
dSWE_MASK = where(MASK .gt. 0.5,dSWE_MASK,dSWE_MASK@_FillValue)
;BASE_MASK = BASE
;BASE_MASK = where(MASK .gt. 0.5,BASE_MASK,BASE_MASK@_FillValue)
;ET_MASK = ET
;ET_MASK = where(MASK .gt. 0.5,ET_MASK,ET_MASK@_FillValue)

tmp = tofloat(SWE_MASK&time)
delete(SWE_MASK&time)
SWE_MASK&time = tmp

system("/bin/rm -f "+model+"_1985to2005_masked.nc")   ; remove any pre-existing file
ncdf = addfile(model+"_1985to2005_masked.nc" ,"c")  ; open output netCDF file

fAtt               = True            ; assign file attributes
fAtt@title         = "NCL Simple Approach to netCDF Creation"
fAtt@source_file   =  "original-file.nc"
fAtt@Conventions   = "None"
fAtt@creation_date = systemfunc ("date")
fileattdef( ncdf, fAtt )            ; copy file attributes


filedimdef(ncdf,"time",-1,True)

;===================================================================
; output variables directly; NCL will call appropriate functions
; to write the meta data associated with each variable
;===================================================================
ncdf->SWE=SWE_MASK
ncdf->dSWE=dSWE_MASK
ncdf->ROF=ROF_MASK
ncdf->PRECIP=PRECIP_MASK
;ncdf->BASE=BASE_MASK
;ncdf->ET=ET_MASK

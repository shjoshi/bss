function MC=readbmat(filename)
fid=fopen(filename,'rb');
r=fread(fid,[1],'uint32');
c=fread(fid,[1],'uint32');
MC=fread(fid,[c r],'float32')';
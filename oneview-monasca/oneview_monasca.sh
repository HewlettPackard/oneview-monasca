if [ $1 = "-I" ]; then
  echo "Installing oneview-monasca..."
  python setup.py install
  echo "Done"
fi

if [ $1 = "-U" ]; then                                                                              
   echo "Installing oneview-monasca..."                                                              
   which_python=$(which python)
   D="bin/python" #Multi Character Delimiter
   
   path=$(echo $which_python | awk -F'bin' '{print $1}' )

   path=$path"/lib/python2.7/site-packages/"

   find $path -maxdepth 1 -name "*oneview_monasca*" -exec rm -rf {} \;
   
   echo "Done" 
fi 

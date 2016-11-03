if [ $1 = "-I" ]; then
  echo "Installing ovm-ironic..."
  python setup.py install
  echo "Done"
fi

if [ $1 = "-U" ]; then                                                                              
   echo "Installing ovm-ironic..."                                                              
   which_python=$(which python)
   D="bin/python" #Multi Character Delimiter
   
   path=$(echo $which_python | awk -F'bin' '{print $1}' )

   path=$path"/lib/python2.7/site-packages/"

   find $path -maxdepth 1 -name "*ovm_ironic*" -exec rm -rf {} \;
   
   echo "Done" 
fi 

>>> import urllib                                       
>>> sock = urllib.urlopen("WebsiteURL") 
>>> htmlSource = sock.read()                            
>>> sock.close()                                        
>>> print htmlSource  

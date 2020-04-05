using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.Text;
using System;
using Android.App;
using Android.OS;
using Android.Support.V7.App;
using Android.Runtime;
using Android.Widget;
using Android.Bluetooth;
using Android.Content.PM;
using Android;
using Android.Support.V4.App;
using Android.Support.V4.Content;
namespace BluetoothApp
{



    [Activity(Label = "@string/app_name", Theme = "@style/AppTheme", MainLauncher = true)]
    public class MainActivity : AppCompatActivity
    {
       
        protected override void OnCreate(Bundle savedInstanceState)
        {
            String targetUuid = "19397893-76dc-4485-8f7c-f43e209ad881";
            String currentSelection = "";

            base.OnCreate(savedInstanceState);
            Xamarin.Essentials.Platform.Init(this, savedInstanceState);
            // Set our view from the "main" layout resource

            SetContentView(Resource.Layout.activity_main);
            const int locationPermissionsRequestCode = 1000;

            var locationPermissions = new[]
            {
                Manifest.Permission.AccessCoarseLocation,
                Manifest.Permission.AccessFineLocation
            };

            // check if the app has permission to access coarse location
            var coarseLocationPermissionGranted =
                ContextCompat.CheckSelfPermission(this, Manifest.Permission.AccessCoarseLocation);

            // check if the app has permission to access fine location
            var fineLocationPermissionGranted =
                ContextCompat.CheckSelfPermission(this, Manifest.Permission.AccessFineLocation);

            // if either is denied permission, request permission from the user
            if (coarseLocationPermissionGranted == Permission.Denied ||
                fineLocationPermissionGranted == Permission.Denied)
            {
                ActivityCompat.RequestPermissions(this, locationPermissions, locationPermissionsRequestCode);
            }

            BluetoothAdapter adapter = BluetoothAdapter.DefaultAdapter;
            ObservableCollection<string> outS = new ObservableCollection<string>();
            if (adapter == null)
               outS.Add("No Bluetooth adapter found.\n");

            else if (!adapter.IsEnabled)
                outS.Add("Bluetooth adapter is not enabled.\n");

            List<int> indexes = new List<int>();
            int index = 0;
            foreach (var dev in adapter.BondedDevices)
            {
                dev.FetchUuidsWithSdp();
                ParcelUuid[] ids = dev.GetUuids();
                bool foundID = false;
                foreach (var i in ids)
                {
                    if (i.Uuid.ToString() == targetUuid)
                    {
                        foundID = true;
                    }
                }
                if (foundID)
                {
                    indexes.Add(index);
                    outS.Add(dev.Name + " " + dev.Address);
                }
                else
                {
                    outS.Add(dev.Name + " " + dev.Address);
                }
                index++;
            }
           
            EditText ssid = FindViewById<EditText>(Resource.Id.ssid);
            EditText password = FindViewById<EditText>(Resource.Id.password);
           
            ListView menu = FindViewById<ListView>(Resource.Id.DeviceList);
            foreach (var ind in indexes)
            {
                //Mark the right device;
            }
            ArrayAdapter<string> initialAdapter = new ArrayAdapter<string>(this, Android.Resource.Layout.SimpleListItem1, outS);
            menu.Adapter = initialAdapter;

            menu.ItemClick += (parent, args) =>
            {
                currentSelection = ((TextView)args.View).Text;


            };

            Button send = FindViewById<Button>(Resource.Id.send);

            send.Click += (parent, args) =>
            {
                var network = ssid.Text;
                var passwd = password.Text;
                try
                {
                    BluetoothDevice target = null;
                    foreach (var dev in adapter.BondedDevices)
                    {
                        
                        if (currentSelection == dev.Name + " " + dev.Address)
                        {
                            target = dev;
                        }
                    }
                    if(target != null && target.FetchUuidsWithSdp()){
                        ParcelUuid[] uuids = target.GetUuids();
                        ParcelUuid foundUuid = null;
                        bool found = false;
                        foreach(var id in uuids)
                        {
                            if (targetUuid == id.Uuid.ToString())
                            {
                                foundUuid = id;
                                found = true;
                            }
                            
                        }
                        
                       
                       
                        if (foundUuid != null && found)
                        {
                            Toast.MakeText(Application, "Trying to connect...", ToastLength.Short).Show();
                            Wait(100);
                            BluetoothSocket bSocket = null;
                            try
                            {
                                bSocket = target.CreateRfcommSocketToServiceRecord(ParcelUuid.FromString(foundUuid.Uuid.ToString()).Uuid);
                                var connection = bSocket.ConnectAsync();
                                connection.Wait(5000);
                                if (bSocket != null && bSocket.IsConnected)
                                {
                                    byte[] msg = Encoding.UTF8.GetBytes(network + " " + passwd);
                                    var write = bSocket.OutputStream.WriteAsync(msg, 0, msg.Length);
                                    write.Wait();
                                    Toast.MakeText(Application, "Credentials were sent succesfully.", ToastLength.Short).Show();

                                }
                                else
                                {
                                    
                                    Toast.MakeText(Application, "Connection timed out.", ToastLength.Short).Show();

                                }
                                

                            }
                            catch
                            {
                                Toast.MakeText(Application, "Connection error.", ToastLength.Short).Show();
                            }

                            
                           
                        }
                        else
                        {
                            Toast.MakeText(Application, "Make sure your raspberrypi is turned on and it is selected from the list.", ToastLength.Long).Show();

                        }
                    }
                   
                }
                catch (Exception ex)
                {
                    
                    Toast.MakeText(this, ex.Message, ToastLength.Short);
                }
                
                }; 

            Button refresh = FindViewById<Button>(Resource.Id.refresh);

            refresh.Click += (parent, args) =>
            {
                ObservableCollection<string> newOut = new ObservableCollection<string>();

                if (adapter == null)
                    newOut.Add("No Bluetooth adapter found.\n");

                else if (!adapter.IsEnabled)
                    newOut.Add("Bluetooth adapter is not enabled.\n");

                List<int> newIndexes = new List<int>();
                int newIndex = 0;
                foreach (var dev in adapter.BondedDevices)
                {
                    dev.FetchUuidsWithSdp();
                    ParcelUuid[] ids = dev.GetUuids();
                    bool foundID = false;
                    foreach(var i in ids)
                    {
                        if(i.Uuid.ToString() == targetUuid)
                        {
                            foundID = true;
                        }
                    }
                    if(foundID)
                    {
                        newIndexes.Add(newIndex);
                        newOut.Add(dev.Name + " " + dev.Address);
                    }
                    else
                    {
                        newOut.Add(dev.Name + " " + dev.Address);
                    }
                    newIndex++;
                }
               
                Toast.MakeText(Application, "Refreshed devices", ToastLength.Short).Show();

                ArrayAdapter<string> newAdapter = new ArrayAdapter<string>(this, Android.Resource.Layout.SimpleListItem1, newOut);
               
                menu.Adapter = newAdapter;
                foreach (var ind in newIndexes)
                {
                    //Mark the right device
                }
            };
        }

    
    
            
        public override void OnRequestPermissionsResult(int requestCode, string[] permissions, [GeneratedEnum] Android.Content.PM.Permission[] grantResults)
        {
            Xamarin.Essentials.Platform.OnRequestPermissionsResult(requestCode, permissions, grantResults);

            base.OnRequestPermissionsResult(requestCode, permissions, grantResults);
        }
    }
}
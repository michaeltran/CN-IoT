using Android.App;
using Android.Widget;
using Android.OS;
using System.Net.Sockets;
using System.Net;
using System;
using System.Threading;
using System.Text;
using Xamarin.Forms;
using Android.Content;

namespace cosc6377android
{
	[Activity(Label = "COSC6377 Project", MainLauncher = true)]
	public class MainActivity : Activity
	{
		protected override void OnCreate(Bundle savedInstanceState)
		{
			base.OnCreate(savedInstanceState);

			// Set our view from the "main" layout resource
			SetContentView(Resource.Layout.Main);
			Xamarin.Forms.Forms.Init(this, savedInstanceState);

			Android.Widget.Button viewButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonView);
			Android.Widget.Button customMessageButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonCustomMessage);
			Android.Widget.Button addPersonButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonAddPerson);
			Android.Widget.EditText editTextFPS = FindViewById<Android.Widget.EditText>(Resource.Id.editTextFPS);

			editTextFPS.Text = "5";

			viewButton.Click += (sender, e) =>
			{
				float FPS = GetFloatValue(editTextFPS);
				if (FPS > 0)
				{
					Intent intentBundle = new Intent(this, typeof(ViewActivity));

					Bundle bundle = new Bundle();
					bundle.PutFloat("FPS", FPS);

					intentBundle.PutExtra("Bundle", bundle);

					StartActivity(intentBundle);
				}
			};

			customMessageButton.Click += (sender, e) =>
			{
				Intent intentBundle = new Intent(this, typeof(CustomMessageActivity));
				StartActivity(intentBundle);
			};

			addPersonButton.Click += (sender, e) =>
			{
				float FPS = GetFloatValue(editTextFPS);
				if (FPS > 0)
				{
					Intent intentBundle = new Intent(this, typeof(AddPersonActivity));

					Bundle bundle = new Bundle();
					bundle.PutFloat("FPS", FPS);

					intentBundle.PutExtra("Bundle", bundle);

					StartActivity(intentBundle);
				}
			};
		}

		private float GetFloatValue(Android.Widget.EditText editText)
		{
			if (float.TryParse(editText.Text, out float n))
			{
				return n;
			}
			return -1;
		}
	}
}


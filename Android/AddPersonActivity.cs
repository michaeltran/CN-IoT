using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

using Android.App;
using Android.Content;
using Android.OS;
using Android.Runtime;
using Android.Views;
using Android.Widget;
using Xamarin.Forms;

namespace cosc6377android
{
	[Activity(Label = "COSC6377 Project")]
	public class AddPersonActivity : Activity
	{
		private bool continueTimer = true;
		private CustomHTTPServer customHTTPServer;

		protected override void OnCreate(Bundle savedInstanceState)
		{
			base.OnCreate(savedInstanceState);

			SetContentView(Resource.Layout.AddPerson);
			Xamarin.Forms.Forms.Init(this, savedInstanceState);

			customHTTPServer = new CustomHTTPServer("34.238.10.126", "5001");

			Android.Widget.ImageView cameraImageView = FindViewById<Android.Widget.ImageView>(Resource.Id.imageViewCamera);
			Android.Widget.EditText firstNameEditText = FindViewById<Android.Widget.EditText>(Resource.Id.editTextFirstName);
			Android.Widget.EditText lastNameEditText = FindViewById<Android.Widget.EditText>(Resource.Id.editTextLastName);
			Android.Widget.EditText minDistanceEditText = FindViewById<Android.Widget.EditText>(Resource.Id.editTextMinDistance);
			Android.Widget.EditText maxDistanceEditText = FindViewById<Android.Widget.EditText>(Resource.Id.editTextMaxDistance);
			Android.Widget.Button addButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonAdd);
			Android.Widget.Button backButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonBack);

			addButton.Click += (sender, e) =>
			{
				if (firstNameEditText.Text != "" && lastNameEditText.Text != "" && int.TryParse(minDistanceEditText.Text, out var minDistance) && int.TryParse(maxDistanceEditText.Text, out var maxDistance))
				{
					customHTTPServer.UploadAddPersonJson(firstNameEditText.Text, lastNameEditText.Text, minDistance, maxDistance);
				}
			};

			backButton.Click += (sender, e) =>
			{
				OnBackPressed();
			};

			Bundle bundle = Intent.GetBundleExtra("Bundle");
			customHTTPServer.UploadFPSJson(Convert.ToInt32(bundle.GetFloat("FPS")));

			Device.StartTimer(TimeSpan.FromSeconds(0.05), () =>
			{
				customHTTPServer.DownloadImageJSON(Resources.DisplayMetrics, cameraImageView, null);
				return this.continueTimer;
			});
		}

		public override void OnBackPressed()
		{
			this.continueTimer = false;
			this.Finish();
		}
	}
}
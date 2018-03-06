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
using System.Threading;

namespace cosc6377android
{
	[Activity(Label = "COSC6377 Project")]
	public class ViewActivity : Activity
	{
		private bool continueTimer = true;
		private CustomHTTPServer customHTTPServer;

		protected override void OnCreate(Bundle savedInstanceState)
		{
			base.OnCreate(savedInstanceState);

			SetContentView(Resource.Layout.View);
			Xamarin.Forms.Forms.Init(this, savedInstanceState);

			customHTTPServer = new CustomHTTPServer("34.238.10.126", "5001");

			Android.Widget.Button authenticateButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonAuthenticate);
			Android.Widget.Button rejectButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonReject);
			Android.Widget.Button backButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonBack);
			Android.Widget.ImageView cameraImageView = FindViewById<Android.Widget.ImageView>(Resource.Id.imageViewCamera);
			Android.Widget.TextView nameTextView = FindViewById<Android.Widget.TextView>(Resource.Id.textViewNameValue);
			Android.Widget.TextView distanceTextView = FindViewById<Android.Widget.TextView>(Resource.Id.textViewDistanceValue);

			cameraImageView.Visibility = ViewStates.Invisible;

			nameTextView.Text = "";
			distanceTextView.Text = "";

			authenticateButton.Click += (sender, e) =>
			{
				customHTTPServer.UploadAuthenticationJson();
			};

			rejectButton.Click += (sender, e) =>
			{
				customHTTPServer.UploadRejectionJson();
			};

			backButton.Click += (sender, e) =>
			{
				OnBackPressed();
			};

			Bundle bundle = Intent.GetBundleExtra("Bundle");
			double fps = 1.0 / bundle.GetFloat("FPS");

			customHTTPServer.UploadFPSJson(Convert.ToInt32(bundle.GetFloat("FPS")));

			Device.StartTimer(TimeSpan.FromSeconds(0.01), () =>
			{
				customHTTPServer.DownloadImageJSON(Resources.DisplayMetrics, cameraImageView, distanceTextView);
				return this.continueTimer;
			});

			Device.StartTimer(TimeSpan.FromSeconds(5), () =>
			{
				customHTTPServer.DownloadDetailsJson(cameraImageView, nameTextView, distanceTextView);
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
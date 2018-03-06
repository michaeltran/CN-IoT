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

namespace cosc6377android
{
	[Activity(Label = "COSC6377 Project")]
	public class CustomMessageActivity : Activity
	{
		CustomHTTPServer customHTTPServer;

		protected override void OnCreate(Bundle savedInstanceState)
		{
			base.OnCreate(savedInstanceState);

			SetContentView(Resource.Layout.CustomMessage);
			Xamarin.Forms.Forms.Init(this, savedInstanceState);

			customHTTPServer = new CustomHTTPServer("34.238.10.126", "5001");

			Android.Widget.EditText sendMessageEditText = FindViewById<Android.Widget.EditText>(Resource.Id.editTextSendMessage);
			Android.Widget.Button sendMessageButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonSendMessage);
			Android.Widget.Button backButton = FindViewById<Android.Widget.Button>(Resource.Id.buttonBack);

			sendMessageButton.Click += (sender, e) =>
			{
				customHTTPServer.UploadMessageJson(sendMessageEditText.Text);
			};

			backButton.Click += (sender, e) =>
			{
				OnBackPressed();
			};
		}
	}
}
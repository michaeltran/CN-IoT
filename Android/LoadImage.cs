using Android.App;
using Android.Widget;
using Android.OS;
using System.Net;
using System.IO;
using System.Text;
using System;
using Android.Graphics;

namespace cosc6377android
{
	class LoadImage
	{
		public static void DownloadImage(ImageView parm)
		{
			WebClient webClient = new WebClient();
			webClient.DownloadDataCompleted += (s, e) => {
				try
				{
					byte[] bytes = e.Result;
					parm.SetImageBitmap(BitmapFactory.DecodeByteArray(bytes, 0, bytes.Length));
				}
				catch
				{
					Console.WriteLine(e.Error);
				}
			};

			Uri url = new Uri("http://54.152.167.198:5001/camera-image.jpg");
			webClient.DownloadDataAsync(url);
		}
	}
}
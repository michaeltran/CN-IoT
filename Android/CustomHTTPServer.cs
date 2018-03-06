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
using System.Net;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Android.Graphics;
using Java.Net;

namespace cosc6377android
{
	public class ImageData
	{
		public string Image { get; set; }
	}

	public class DetailsData
	{
		public string ID { get; set; }
		public string FirstName { get; set; }
		public string LastName { get; set; }
		public string MinDistance { get; set; }
		public string MaxDistance { get; set; }
		public string Distance { get; set; }
	}

	public class CustomHTTPServer
	{
		private string _ip;
		private string _port;

		private DetailsData _detailsData;

		public CustomHTTPServer(string ip, string port)
		{
			_ip = ip;
			_port = port;
		}

		public void DownloadImageJSON(Android.Util.DisplayMetrics metrics, ImageView imageView, TextView textViewDistance)
		{
			using (WebClient webClient = new WebClient())
			{
				Uri url = new Uri(string.Format("http://{0}:{1}/image.json", _ip, _port));
				try
				{
					byte[] bytes = webClient.DownloadData(url);

					ImageData imageData = JsonConvert.DeserializeObject<ImageData>(System.Text.Encoding.UTF8.GetString(bytes));

					byte[] imageBytes = Convert.FromBase64String(imageData.Image);
					Bitmap bitmap = BitmapFactory.DecodeByteArray(imageBytes, 0, imageBytes.Length);

					double resizeFactor = (double)metrics.WidthPixels / bitmap.Width;
					int resizeWidth = Convert.ToInt32(bitmap.Width * resizeFactor);
					int resizeHeight = Convert.ToInt32(bitmap.Height * resizeFactor);

					Bitmap scaledBitmap = Bitmap.CreateScaledBitmap(bitmap, resizeWidth, resizeHeight, false);
					imageView.SetImageBitmap(scaledBitmap);
					/*
					if (textViewDistance != null)
						textViewDistance.Text = imageData.Distance + "mm";
					*/
				}
				catch (Exception ex)
				{
					Console.WriteLine(ex.Message);
				}
			}
		}

		public void DownloadDetailsJson(ImageView imageView, TextView textViewName, TextView textViewDistance)
		{
			using (WebClient webClient = new WebClient())
			{
				Uri url = new Uri(string.Format("http://{0}:{1}/details.json", _ip, _port));
				try
				{
					byte[] bytes = webClient.DownloadData(url);

					_detailsData = JsonConvert.DeserializeObject<DetailsData>(System.Text.Encoding.UTF8.GetString(bytes));

					if (_detailsData.MinDistance == "" || _detailsData.MinDistance == null)
						_detailsData.MinDistance = "-1";
					if (_detailsData.MaxDistance == "" || _detailsData.MaxDistance == null)
						_detailsData.MaxDistance = "-1";
					if (_detailsData.Distance == "" || _detailsData.Distance == null)
						_detailsData.Distance = "0";

					
					if (Convert.ToDouble(_detailsData.MinDistance) <= Convert.ToDouble(_detailsData.Distance) && Convert.ToDouble(_detailsData.Distance) <= Convert.ToDouble(_detailsData.MaxDistance))
						imageView.Visibility = ViewStates.Visible;
					else
						imageView.Visibility = ViewStates.Invisible;
					
					textViewName.Text = _detailsData.FirstName + " " + _detailsData.LastName;
					if (textViewDistance != null)
						textViewDistance.Text = _detailsData.Distance + "mm";
				}
				catch (Exception ex)
				{
					Console.WriteLine(ex.Message);
				}
			}
		}

		public void UploadAddPersonJson(string firstName, string lastName, int minDistance, int maxDistance)
		{
			using (WebClient webClient = new WebClient())
			{
				webClient.UploadStringCompleted += (s, e) =>
				{
					try
					{
						string theString = e.Result;
					}
					catch
					{
						Console.WriteLine(e.Error);
					}
				};

				JArray array = new JArray();
				Newtonsoft.Json.Linq.JValue text = new Newtonsoft.Json.Linq.JValue("Manual text");
				Newtonsoft.Json.Linq.JValue date = new Newtonsoft.Json.Linq.JValue(new DateTime(2000, 5, 23));
				array.Add(text);
				array.Add(date);

				Uri url = new Uri(string.Format("http://{0}:{1}/AddPerson?firstname={2}&amp;lastname={3}&amp;mindistance={4}&amp;maxdistance={5}", 
					_ip, _port, URLEncoder.Encode(firstName, "UTF-8"), URLEncoder.Encode(lastName, "UTF-8"), URLEncoder.Encode(minDistance.ToString(), "UTF-8"), URLEncoder.Encode(maxDistance.ToString(), "UTF-8")));
				webClient.Headers["Content-Type"] = "application/json";
				webClient.UploadDataAsync(url, Encoding.ASCII.GetBytes(array.ToString()));
			}
		}

		public void UploadMessageJson(string message)
		{
			using (WebClient webClient = new WebClient())
			{
				webClient.UploadStringCompleted += (s, e) =>
				{
					try
					{
						string theString = e.Result;
					}
					catch
					{
						Console.WriteLine(e.Error);
					}
				};

				JArray array = new JArray();
				Newtonsoft.Json.Linq.JValue text = new Newtonsoft.Json.Linq.JValue("Manual text");
				Newtonsoft.Json.Linq.JValue date = new Newtonsoft.Json.Linq.JValue(new DateTime(2000, 5, 23));
				array.Add(text);
				array.Add(date);

				Uri url = new Uri(string.Format("http://{0}:{1}/Authenticate?message={2}", _ip, _port, URLEncoder.Encode(message, "UTF-8")));
				webClient.Headers["Content-Type"] = "application/json";
				webClient.UploadDataAsync(url, Encoding.ASCII.GetBytes(array.ToString()));
			}
		}

		public void UploadAuthenticationJson()
		{
			if (_detailsData != null && (_detailsData.ID != null || _detailsData.ID != ""))
			{
				string message = string.Format("Welcome home, {0} {1}", _detailsData.FirstName, _detailsData.LastName);

				UploadMessageJson(message);
			}
		}

		public void UploadRejectionJson()
		{
			if (_detailsData != null && (_detailsData.ID != null || _detailsData.ID != ""))
			{
				string message = "System does not recognize you, try again.";

				UploadMessageJson(message);
			}
		}

		public void UploadFPSJson(int FPS)
		{
			using (WebClient webClient = new WebClient())
			{
				webClient.UploadStringCompleted += (s, e) =>
				{
					try
					{
						string theString = e.Result;
					}
					catch
					{
						Console.WriteLine(e.Error);
					}
				};

				JArray array = new JArray();
				Newtonsoft.Json.Linq.JValue text = new Newtonsoft.Json.Linq.JValue("Manual text");
				Newtonsoft.Json.Linq.JValue date = new Newtonsoft.Json.Linq.JValue(new DateTime(2000, 5, 23));
				array.Add(text);
				array.Add(date);

				Uri url = new Uri(string.Format("http://{0}:{1}/FPS?fps={2}", _ip, _port, URLEncoder.Encode(FPS.ToString(), "UTF-8")));
				webClient.Headers["Content-Type"] = "application/json";
				webClient.UploadDataAsync(url, Encoding.ASCII.GetBytes(array.ToString()));
			}
		}
	}
}
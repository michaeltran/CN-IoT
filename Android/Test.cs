using System.Text;
using System;
using System.Threading.Tasks;
using System.Net;
using System.IO;
using System.Json;

namespace cosc6377android
{
	public static class Test
	{
		public static void TestMethod()
		{
			Console.WriteLine("hello");
		}

		public static async Task TestMethod2()
		{
			TestA testA = new TestA();
			JsonValue json = await testA.FetchWeatherAsync("");
		}
	}

	public class TestA
	{
		// Gets weather data from the passed URL.
		public async Task<JsonValue> FetchWeatherAsync(string url)
		{
			// Create an HTTP web request using the URL:
			HttpWebRequest request = (HttpWebRequest)HttpWebRequest.Create(new Uri(url));
			request.ContentType = "application/json";
			request.Method = "GET";

			// Send the request to the server and wait for the response:
			using (WebResponse response = await request.GetResponseAsync())
			{
				// Get a stream representation of the HTTP web response:
				using (Stream stream = response.GetResponseStream())
				{
					// Use this stream to build a JSON document object:
					JsonValue jsonDoc = await Task.Run(() => JsonObject.Load(stream));
					Console.Out.WriteLine("Response: {0}", jsonDoc.ToString());

					// Return the JSON document:
					return jsonDoc;
				}
			}
		}
	}
}
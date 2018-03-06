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
using System.Net.Sockets;
using System.Threading;
using System.IO;
using System.Json;

namespace cosc6377android
{
	class Test2
	{
		public static void runtest()
		{
			IPAddress ipAddress = Dns.GetHostEntry("54.152.167.198").AddressList[0];

			IPEndPoint ipEndPoint = new IPEndPoint(ipAddress, 5000);

			Socket clientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

			IAsyncResult asyncConnect = clientSocket.BeginConnect(
			  ipEndPoint,
			  new AsyncCallback(connectCallback),
			  clientSocket);

			Console.Write("Connection in progress.");
			//if (writeDot(asyncConnect) == true)
			//{
			//	// allow time for callbacks to
			//	// finish before the program ends
			//	Thread.Sleep(3000);
			//}

		}

		// used to pass state information to delegate
		class StateObject
		{
			internal byte[] sBuffer;
			internal Socket sSocket;
			internal StateObject(int size, Socket sock)
			{
				sBuffer = new byte[size];
				sSocket = sock;
			}
		}

		public static void connectCallback(IAsyncResult asyncConnect)
		{
			Socket clientSocket =
			  (Socket)asyncConnect.AsyncState;
			clientSocket.EndConnect(asyncConnect);
			// arriving here means the operation completed
			// (asyncConnect.IsCompleted = true) but not
			// necessarily successfully
			if (clientSocket.Connected == false)
			{
				Console.WriteLine(".client is not connected.");
				return;
			}
			else Console.WriteLine(".client is connected.");

			JsonObject jsonObject = new JsonObject();
			jsonObject["Type"] = "Test";

			string request = jsonObject.ToString();
			int reqLen = request.Length;
			int reqLenH2N = IPAddress.HostToNetworkOrder(reqLen);
			byte[] reqLenArray = BitConverter.GetBytes(reqLenH2N);
			byte[] reqArray = Encoding.ASCII.GetBytes(request);
			//byte[] sendBuffer = Encoding.ASCII.GetBytes(request);


			byte[] sendBuffer = Combine(reqLenArray, reqArray);

			//clientSocket.Send(reqLenArray, 4, System.Net.Sockets.SocketFlags.None);
			//clientSocket.Send(sendBuffer, reqLen, System.Net.Sockets.SocketFlags.None);
			IAsyncResult asyncSend = clientSocket.BeginSend(
			  sendBuffer,
			  0,
			  sendBuffer.Length,
			  SocketFlags.None,
			  new AsyncCallback(sendCallback),
			  clientSocket);

			Console.Write("Sending data.");
			//writeDot(asyncSend);
		}

		public static byte[] Combine(byte[] first, byte[] second)
		{
			byte[] ret = new byte[first.Length + second.Length];
			Buffer.BlockCopy(first, 0, ret, 0, first.Length);
			Buffer.BlockCopy(second, 0, ret, first.Length, second.Length);
			return ret;
		}

		public static void sendCallback(IAsyncResult asyncSend)
		{
			Socket clientSocket = (Socket)asyncSend.AsyncState;
			int bytesSent = clientSocket.EndSend(asyncSend);
			Console.WriteLine(
			  ".{0} bytes sent.",
			  bytesSent.ToString());

			StateObject stateObject =
			  new StateObject(4, clientSocket);

			// this call passes the StateObject because it
			// needs to pass the buffer as well as the socket
			IAsyncResult asyncReceive =
			  clientSocket.BeginReceive(
				stateObject.sBuffer,
				0,
				stateObject.sBuffer.Length,
				SocketFlags.None,
				new AsyncCallback(receiveObjectCallback),
				stateObject);

			Console.Write("Receiving response.");
			//writeDot(asyncReceive);
		}

		//public static void sendCallback(IAsyncResult asyncSend)
		//{
		//	Socket clientSocket = (Socket)asyncSend.AsyncState;
		//	int bytesSent = clientSocket.EndSend(asyncSend);
		//	Console.WriteLine(
		//	  ".{0} bytes sent.",
		//	  bytesSent.ToString());

		//	StateObject stateObject =
		//	  new StateObject(4, clientSocket);

		//	// this call passes the StateObject because it
		//	// needs to pass the buffer as well as the socket
		//	IAsyncResult asyncReceive =
		//	  clientSocket.BeginReceive(
		//		stateObject.sBuffer,
		//		0,
		//		stateObject.sBuffer.Length,
		//		SocketFlags.None,
		//		new AsyncCallback(receiveCallback),
		//		stateObject);

		//	Console.Write("Receiving response.");
		//	//writeDot(asyncReceive);
		//}

		public static void receiveCallback(IAsyncResult asyncReceive)
		{
			StateObject stateObject =
			 (StateObject)asyncReceive.AsyncState;

			int bytesReceived =
			  stateObject.sSocket.EndReceive(asyncReceive);

			var temp = Encoding.ASCII.GetString(stateObject.sBuffer);

			Console.WriteLine(
			  ".{0} bytes received: {1}{2}{2}Shutting down.",
			  bytesReceived.ToString(),
			  Encoding.ASCII.GetString(stateObject.sBuffer),
			  System.Environment.NewLine);

			//stateObject.sSocket.Shutdown(SocketShutdown.Both);
			//stateObject.sSocket.Close();
		}

		public static void receiveObjectCallback(IAsyncResult asyncReceive)
		{
			StateObject stateObject =
			 (StateObject)asyncReceive.AsyncState;

			int bytesReceived =
			  stateObject.sSocket.EndReceive(asyncReceive);

			string totalBytes = Encoding.ASCII.GetString(stateObject.sBuffer);

			StateObject newStateObject =
			  new StateObject(Convert.ToInt32(totalBytes), stateObject.sSocket);

			IAsyncResult asyncReceive2 =
			  stateObject.sSocket.BeginReceive(
				newStateObject.sBuffer,
				0,
				newStateObject.sBuffer.Length,
				SocketFlags.None,
				new AsyncCallback(receiveObjectCallback2),
				newStateObject);
		}

		public static void receiveObjectCallback2(IAsyncResult asyncReceive)
		{
			StateObject stateObject =
			 (StateObject)asyncReceive.AsyncState;

			int bytesReceived =
			  stateObject.sSocket.EndReceive(asyncReceive);

			var temp = Encoding.ASCII.GetString(stateObject.sBuffer);

			Console.WriteLine(
			  ".{0} bytes received: {1}{2}{2}Shutting down.",
			  bytesReceived.ToString(),
			  Encoding.ASCII.GetString(stateObject.sBuffer),
			  System.Environment.NewLine);
		}

		// times out after 2 seconds but operation continues
		internal static bool writeDot(IAsyncResult ar)
		{
			int i = 0;
			while (ar.IsCompleted == false)
			{
				if (i++ > 20)
				{
					Console.WriteLine("Timed out.");
					return false;
				}
				Console.Write(".");
				Thread.Sleep(100);
			}
			return true;
		}
	}
}
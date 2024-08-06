using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class RobotUDPClient : MonoBehaviour
{
    #region Variables



	[SerializeField]
	private string _robotIP = "192.168.4.1";
	[SerializeField]
	private int _robotPort = 1234;

	private bool _connected = false;
	private bool _unlocked = true;
	private Thread _receiveThread;
	byte[] sendData;
    byte[] recvData = new byte[4096];
	byte[] byteArray;
	int recvLen;

	public bool SendCmd = true;

	Socket ClientSocket;
	EndPoint ServerEndPoint;
	Thread connectThread;

	#endregion

	#region MonoBehaviour
    private void Start(){
        SetConnect(true);
    }
    private void OnApplicationQuit()
	{
        SetConnect(false);
    }
    #endregion

    #region Methods
    public void SetRobotIP(string value)
    {
        _robotIP = value;
		PlayerPrefs.SetString("_robotIP", _robotIP);
		PlayerPrefs.Save();
		Debug.Log(value);
	}
    public void SetRobotPort(string value)
    {
        _robotPort = int.Parse(value);
		PlayerPrefs.SetInt("_robotPort", _robotPort);
		PlayerPrefs.Save();
		Debug.Log(value);
	}
    public void SetConnect(bool value)
    {
        if (value)
		{
            try
            {

				ServerEndPoint = new IPEndPoint(IPAddress.Parse(_robotIP), _robotPort);
				ClientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);

				ClientSocket.SendTimeout = 5000;
				ClientSocket.ReceiveTimeout = 5000;

				byteArray = new byte[2];
				byteArray[0] = 0;
				byteArray[1] = 1;
				ClientSocket.SendTo(byteArray, byteArray.Length, SocketFlags.None, ServerEndPoint);

				connectThread = new Thread(new ThreadStart(ServerMsgHandler));
				connectThread.Start();
                _connected = true;
			}
			catch (Exception ex)
			{
				print(ex);
			}
		}
        else
		{
			_connected = false;
			byteArray = new byte[2];
			byteArray[0] = 0;
			byteArray[1] = 0;
			ClientSocket.SendTo(byteArray, byteArray.Length, SocketFlags.None, ServerEndPoint);
		}
    }

    private void ServerMsgHandler()
    {
		while(_connected){
			recvLen = ClientSocket.ReceiveFrom(recvData, ref ServerEndPoint);
			if (recvLen > 0)
			{
				Vector3 robotPos = new Vector3(BitConverter.ToSingle(recvData, 0), BitConverter.ToSingle(recvData, 4), BitConverter.ToSingle(recvData, 8));
				Quaternion robotRot = new Quaternion(BitConverter.ToSingle(recvData, 12), BitConverter.ToSingle(recvData, 16), BitConverter.ToSingle(recvData, 20), BitConverter.ToSingle(recvData, 24));
				Debug.Log("Robot Pos: " + robotPos + " Robot Rot: " + robotRot);
			}
		}
    }
	public bool IsConnected() { return _connected; }
    public void SendVelCmd(float linear_vel, float angular_vel)
    {
        if (!_connected) {
            Debug.Log("Not connected to robot");
            return;
        }
        try
        {
            byteArray = new byte[sizeof(float) * 2 + 1];
            byteArray[0] = 1;
            Buffer.BlockCopy(BitConverter.GetBytes(linear_vel), 0, byteArray, 1, 4);
            Buffer.BlockCopy(BitConverter.GetBytes(angular_vel), 0, byteArray, 5, 4);
            ClientSocket.SendTo(byteArray, byteArray.Length, SocketFlags.None, ServerEndPoint);
        }
        catch (Exception e)
        {
            Debug.Log(e.ToString());
        }
    }
	#endregion
}

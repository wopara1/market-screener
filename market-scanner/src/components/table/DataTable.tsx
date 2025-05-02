import { Input } from "@mui/joy";
import { BiSearch } from "react-icons/bi";
import HoverEl from "../hover-el/HoverEl";
import { GrMoreVertical } from "react-icons/gr";
import { useEffect, useRef, useState } from "react";
import WebSocketComponent from "../../wsocket/client";

type PayloadType = { exchange: string; filters: { ticker: string[] } };
type PayloadSecond = {
  ask_price: number;
  ask_size: number;
  bid_price: number;
  bid_size: number;
  exchange: string;
  last_price: null | number;
  last_size: null | number;
  ticker: string;
  timestamp: number;
  type: string;
};

const DataTable = () => {
  const [data, setData] = useState<{ event: string; payload: PayloadSecond }[]>(
    []
  );
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");

      // Send a JSON-formatted event payload to the backend
      ws.send(
        JSON.stringify({
          event: "subscribe",
          payload: { exchange: "crypto", filters: { ticker: ["BTCUSD"] } },
        })
      );
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (!message.payload || !message.payload.ticker) return;
        // console.log("Received:", message);
        setData((prev) => {
          const updated = [...prev, message];
          return updated.slice(-20); // Only keep the last 10
        });
      } catch (err) {
        console.error("Error parsing WebSocket message", err);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return () => {
      ws.close();
    };
  }, []);
  console.log({ data });

  // Optional: method to dynamically send events
  const sendEvent = (event: string, payload: PayloadType) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ event, payload }));
    }
  };

  // useEffect(() => {
  //   sendEvent("subscribe", {
  //     exchange: "crypto",
  //     filters: { ticker: ["BTCUSD"] },
  //   });
  // }, []);
  return (
    <div>
      <div className="w-full overflow-x-auto">
        <table>
          <thead>
            <tr className="uppercase border border-gray-200">
              <td className="p-2 px-3 min-w-28 text-sm border-r border-gray-200">
                <div className="flex items-center gap-8">
                  <div className="text-sm">
                    <p className="text-xs text-gray-400">Ticker</p>
                    <p className="text-xs">5093 matches</p>
                  </div>
                  <Input
                    startDecorator={<BiSearch />}
                    sx={{ width: "130px" }}
                  />
                </div>
              </td>
              <HoverEl text="price" />
              <HoverEl text="chg %" />
              <HoverEl text="chg" />
              <HoverEl text="high" />
              <HoverEl text="low" />
              <HoverEl text="vol" />
              <HoverEl
                text="vol 24h
                in usd"
              />
              <HoverEl
                text="vol 24h
                chg %"
              />
              <HoverEl text="technical rating" />
              <HoverEl text="exchange" />
              <td className="text-center p-2 px-3 border-r border-gray-200 text-sm">
                <GrMoreVertical />
              </td>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => {
              const event = item.event;
              const payload = item.payload;
              // if (typeof payload =)
              return (
                <tr key={idx}>
                  <td className="uppercase">{payload.ticker}</td>
                  <td>{payload.ask_price}</td>
                  <td className="text-green-700">{payload.ask_price}%</td>
                  <td>{payload.bid_size}</td>
                  <td>{payload.last_price}</td>
                  <td>{payload.last_size}</td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td>{payload.exchange}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {/* <WebSocketComponent /> */}
    </div>
  );
};

export default DataTable;

import { Input } from "@mui/joy";
import "./App.css";
import { BiSearch } from "react-icons/bi";
import { VscSettings } from "react-icons/vsc";
import { useState } from "react";
import { GrMoreVertical } from "react-icons/gr";
import  WebSocketComponent from "./wsocket/client";

function App() {
  return (
    <>
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
            <tr>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
          </tbody>
        </table>
      </div>
      <WebSocketComponent/>
    </>
  );
}

export default App;

const HoverEl = ({ text }: { text: string }) => {
  const [showHover, setShowHover] = useState(false);
  return (
    <td
      className="text-center p-2 px-3 min-w-28 border-r border-gray-200 text-sm relative"
      onMouseOver={() => setShowHover(true)}
      onMouseLeave={() => setShowHover(false)}
    >
      {showHover && (
        <div className="absolute inset-0 bg-gray-300 opacity-50 flex justify-end">
          <div className="w-fit absolute inset-y-0 right-0 self-center px-1 border-l flex h-full text-black items-center border-gray-400 hover:bg-gray-400">
            <VscSettings className="rotate-90" size={18} />
          </div>
        </div>
      )}
      {text}
    </td>
  );
};

import { useState } from "react";
import { VscSettings } from "react-icons/vsc";

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

export default HoverEl;

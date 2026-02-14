import { AuthContextType } from "@/shared/types";
import { createContext } from "react";


export const AuthContext = createContext<AuthContextType | null>(null);
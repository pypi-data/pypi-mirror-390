import"./CWj6FrbW.js";import"./CN51-NxK.js";import{b as Be,g as Oe,q as he,u as P,v as Ke,e as ze,j as d,i as f,k as u,c as r,r as a,l as O,a as p,t as g,w as l,s as c,p as Je,f as h,m as b,x as K,n as w}from"./CvTLsZlf.js";import{i as Qe}from"./B3D73U8p.js";import{r as z,a as J}from"./CPzR4-ix.js";import{b as Q}from"./BpTtYi1u.js";import{b as ge}from"./Cz9Z7v2M.js";import{p as Ve}from"./Bfc47y5P.js";import{i as Xe}from"./CNVL70pO.js";import{p as v}from"./DBxQAEQJ.js";import{a as xe,s as Ze}from"./DzS5ldT-.js";import{g as et}from"./B3JesTH8.js";import{u as tt}from"./BhUNH95W.js";import{C as rt}from"./CmqIt7kY.js";import{C as at}from"./CJhxu3Yk.js";import{C as st}from"./B0itHwGp.js";import{T as A}from"./k6hQMChD.js";import{L as ot}from"./BzcWeUV3.js";import{A as it}from"./KcmNtx4b.js";var lt=h('<button class="w-full text-left text-sm py-1.5 px-1 rounded-lg dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-gray-850" type="button"><!></button>'),nt=h('<input class="w-full text-2xl font-medium bg-transparent outline-hidden font-primary" type="text" required/>'),dt=h('<div class="text-sm text-gray-500 shrink-0"> </div>'),ut=h('<input class="w-full text-sm disabled:text-gray-500 bg-transparent outline-hidden" type="text" required/>'),ct=h('<input class="w-full text-sm bg-transparent outline-hidden" type="text" required/>'),mt=h('<div class="text-sm text-gray-500"><div class=" bg-yellow-500/20 text-yellow-700 dark:text-yellow-200 rounded-lg px-4 py-3"><div> </div> <ul class=" mt-1 list-disc pl-4 text-xs"><li> </li> <li> </li></ul></div> <div class="my-3"> </div></div>'),ft=h('<!> <div class=" flex flex-col justify-between w-full overflow-y-auto h-full"><div class="mx-auto w-full md:px-0 h-full"><form class=" flex flex-col max-h-[100dvh] h-full"><div class="flex flex-col flex-1 overflow-auto h-0 rounded-lg"><div class="w-full mb-2 flex flex-col gap-0.5"><div class="flex w-full items-center"><div class=" shrink-0 mr-2"><!></div> <div class="flex-1"><!></div> <div class="self-center shrink-0"><button class="bg-gray-50 hover:bg-gray-100 text-black dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-white transition px-2 py-1 rounded-full flex gap-1 items-center" type="button"><!> <div class="text-sm font-medium shrink-0"> </div></button></div></div> <div class=" flex gap-2 px-1 items-center"><!> <!></div></div> <div class="mb-2 flex-1 overflow-auto h-0 rounded-lg"><!></div> <div class="pb-3 flex justify-between"><div class="flex-1 pr-3"><div class="text-xs text-gray-500 line-clamp-2"><span class=" font-semibold dark:text-gray-200"> </span> <br/>— <span class=" font-medium dark:text-gray-400"> </span></div></div> <button class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full" type="submit"> </button></div></div></form></div></div> <!>',1);function Nt(ye,m){Be(m,!1);const I=()=>xe(tt,"$user",V),e=()=>xe(we,"$i18n",V),[V,be]=Ze(),we=Oe("i18n");let k=b(null),D=b(!1),N=b(!1),x=v(m,"edit",8,!1),X=v(m,"clone",8,!1),ke=v(m,"onSave",8,()=>{}),$=v(m,"id",12,""),y=v(m,"name",12,""),C=v(m,"meta",28,()=>({description:""})),_=v(m,"content",12,""),M=v(m,"accessControl",28,()=>({})),E=b("");const $e=()=>{f(E,_())};let T=b(),Ce=`import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        pass

    # Add your custom tools using pure Python code here, make sure to add type hints and descriptions
	
    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """

        # Do not include a descrption for __user__ as it should not be shown in the tool's specification
        # The session user object will be passed as a parameter when the function is called

        print(__user__)
        result = ""

        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"

        if result == "":
            result = "User: Unknown"

        return result

    def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        """

        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")  # Using 12-hour format with AM/PM
        current_date = now.strftime(
            "%A, %B %d, %Y"
        )  # Full weekday, month name, day, and year

        return f"Current Date and Time = {current_date}, {current_time}"

    def calculator(
        self,
        equation: str = Field(
            ..., description="The mathematical equation to calculate."
        ),
    ) -> str:
        """
        Calculate the result of an equation.
        """

        # Avoid using eval in production code
        # https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
        try:
            result = eval(equation)
            return f"{equation} = {result}"
        except Exception as e:
            print(e)
            return "Invalid equation"

    def get_current_weather(
        self,
        city: str = Field(
            "New York, NY", description="Get the current weather for a given city."
        ),
    ) -> str:
        """
        Get the current weather for a given city.
        """

        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return (
                "API key is not set in the environment variable 'OPENWEATHER_API_KEY'."
            )

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",  # Optional: Use 'imperial' for Fahrenheit
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            data = response.json()

            if data.get("cod") != 200:
                return f"Error fetching weather data: {data.get('message')}"

            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            return f"Weather in {city}: {temperature}°C"
        except requests.RequestException as e:
            return f"Error fetching weather data: {str(e)}"
`;const Ee=async()=>{ke()({id:$(),name:y(),meta:C(),content:_(),access_control:M()})},Z=async()=>{if(d(T)){_(d(E)),await K();const t=await d(T).formatPythonCodeHandler();await K(),_(d(E)),await K(),t&&Ee()}};he(()=>P(_()),()=>{_()&&$e()}),he(()=>(P(y()),P(x()),P(X())),()=>{y()&&!x()&&!X()&&$(y().replace(/\s+/g,"_").toLowerCase())}),Ke(),Xe();var ee=ft(),te=ze(ee);{let t=w(()=>(I(),l(()=>{var i,n,s,o;return((s=(n=(i=I())==null?void 0:i.permissions)==null?void 0:n.sharing)==null?void 0:s.public_tools)||((o=I())==null?void 0:o.role)==="admin"})));it(te,{accessRoles:["read","write"],get allowPublic(){return d(t)},get show(){return d(N)},set show(i){f(N,i)},get accessControl(){return M()},set accessControl(i){M(i)},$$legacy:!0})}var j=u(te,2),re=r(j),q=r(re),ae=r(q),H=r(ae),S=r(H),W=r(S),Te=r(W);{let t=w(()=>(e(),l(()=>e().t("Back"))));A(Te,{get content(){return d(t)},children:(i,n)=>{var s=lt(),o=r(s);st(o,{strokeWidth:"2.5"}),a(s),O("click",s,()=>{et("/workspace/tools")}),p(i,s)},$$slots:{default:!0}})}a(W);var F=u(W,2),qe=r(F);{let t=w(()=>(e(),l(()=>e().t("e.g. My Tools"))));A(qe,{get content(){return d(t)},placement:"top-start",children:(i,n)=>{var s=nt();z(s),g(o=>J(s,"placeholder",o),[()=>(e(),l(()=>e().t("Tool Name")))]),Q(s,y),p(i,s)},$$slots:{default:!0}})}a(F);var se=u(F,2),R=r(se),oe=r(R);ot(oe,{strokeWidth:"2.5",className:"size-3.5"});var ie=u(oe,2),Pe=r(ie,!0);a(ie),a(R),a(se),a(S);var le=u(S,2),ne=r(le);{var Ae=t=>{var i=dt(),n=r(i,!0);a(i),g(()=>c(n,$())),p(t,i)},Ie=t=>{{let i=w(()=>(e(),l(()=>e().t("e.g. my_tools"))));A(t,{className:"w-full",get content(){return d(i)},placement:"top-start",children:(n,s)=>{var o=ut();z(o),g(L=>{J(o,"placeholder",L),o.disabled=x()},[()=>(e(),l(()=>e().t("Tool ID")))]),Q(o,$),p(n,o)},$$slots:{default:!0}})}};Qe(ne,t=>{x()?t(Ae):t(Ie,!1)})}var De=u(ne,2);{let t=w(()=>(e(),l(()=>e().t("e.g. Tools for performing various operations"))));A(De,{className:"w-full self-center items-center flex",get content(){return d(t)},placement:"top-start",children:(i,n)=>{var s=ct();z(s),g(o=>J(s,"placeholder",o),[()=>(e(),l(()=>e().t("Tool Description")))]),Q(s,()=>C().description,o=>C(C().description=o,!0)),p(i,s)},$$slots:{default:!0}})}a(le),a(H);var U=u(H,2),Ne=r(U);ge(rt(Ne,{get value(){return _()},lang:"python",boilerplate:Ce,onChange:t=>{f(E,t)},onSave:async()=>{d(k)&&d(k).requestSubmit()},$$legacy:!0}),t=>f(T,t),()=>d(T)),a(U);var de=u(U,2),Y=r(de),ue=r(Y),G=r(ue),Me=r(G,!0);a(G);var ce=u(G),me=u(ce,3),je=r(me,!0);a(me),a(ue),a(Y);var fe=u(Y,2),He=r(fe,!0);a(fe),a(de),a(ae),a(q),ge(q,t=>f(k,t),()=>d(k)),a(re),a(j);var Se=u(j,2);at(Se,{get show(){return d(D)},set show(t){f(D,t)},$$events:{confirm:()=>{Z()}},children:(t,i)=>{var n=mt(),s=r(n),o=r(s),L=r(o,!0);a(o);var ve=u(o,2),B=r(ve),We=r(B,!0);a(B);var _e=u(B,2),Fe=r(_e,!0);a(_e),a(ve),a(s);var pe=u(s,2),Re=r(pe,!0);a(pe),a(n),g((Ue,Ye,Ge,Le)=>{c(L,Ue),c(We,Ye),c(Fe,Ge),c(Re,Le)},[()=>(e(),l(()=>e().t("Please carefully review the following warnings:"))),()=>(e(),l(()=>e().t("Tools have a function calling system that allows arbitrary code execution."))),()=>(e(),l(()=>e().t("Do not install tools from sources you do not fully trust."))),()=>(e(),l(()=>e().t("I acknowledge that I have read and I understand the implications of my action. I am aware of the risks associated with executing arbitrary code and I have verified the trustworthiness of the source.")))]),p(t,n)},$$slots:{default:!0},$$legacy:!0}),g((t,i,n,s,o)=>{c(Pe,t),c(Me,i),c(ce,` ${n??""} `),c(je,s),c(He,o)},[()=>(e(),l(()=>e().t("Access"))),()=>(e(),l(()=>e().t("Warning:"))),()=>(e(),l(()=>e().t("Tools are a function calling system with arbitrary code execution"))),()=>(e(),l(()=>e().t("don't install random tools from sources you don't trust."))),()=>(e(),l(()=>e().t("Save")))]),O("click",R,()=>{f(N,!0)}),O("submit",q,Ve(()=>{x()?Z():f(D,!0)})),p(ye,ee),Je(),be()}export{Nt as T};
//# sourceMappingURL=CCZKDGdt.js.map

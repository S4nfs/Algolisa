import React, { useCallback, useMemo, useState } from 'react';
import UseMemoUseCallbackChildComponent from './23_UseMemoUseCallbackChildComponent';

function UseMemoUseCallback() {
    const [num, setNum] = useState(0);
    //Problem: Child component get rendered everytime the state changes
    //✅Solution: useMemo but it won't handle functions and re-renderes the child component again as useMemo returns memoized value

    //const getChildComp = useMemo(() => <UseMemoUseCallbackChildComponent handleUpdateNum={handleUpdateNum} />, [])

    //Problem: Every time the parent component gets re-rendered, handleUpdateNum function got re-created. here in handleUpdateNum useMemo won't work. Because every time the parent component gets re-rendered, handleUpdateNum function got re-created.
    //✅Solution: There useCallback comes into the picture which returns us memoized function.


    const handleUpdateNum = useCallback(() => {
        //no re-rendering brother
    }, []);

    const getChildComp = useMemo(() => <UseMemoUseCallbackChildComponent handleUpdateNum={handleUpdateNum} />, [handleUpdateNum])
    return (
        <div>
            <h1>UseMemo & UseCallback Hooks</h1>
            <h1>{num}</h1>
            {getChildComp}
            <button onClick={() => setNum(num + 1)}> Addition </button>
        </div>
    );
}


export default UseMemoUseCallback;

import '@/styles/modal.css';

import { createPortal } from 'react-dom';
import { ModalProps } from '@/shared/types';
import { useFrequentlyUsedConditionsHook } from '@/features/todo/hooks/useTodo';

export default function FrequentlyConditionModal({isOpen, onClose, onApply} : ModalProps) {
  
  // 훅은 항상 최상단에 (조건문 이전) - isOpen(enabled 옵션으로 사용하여 fetch 시점 제어)
  const {conditionList, isLoading} = useFrequentlyUsedConditionsHook(isOpen);
  
  // isOpen이 false면 렌더링 안 함
  if (!isOpen) return null;

  const modalRoot = document.getElementById("modal-root");

  if (!modalRoot) return null;

  

  return createPortal(
    <div className="modal-overlay">
      <div className="modal-content">

        <div className="container condition-list w-75">
          <h2 className="text-center my-6">저장된 조건</h2>
          <table className="table table-striped">
            <thead>
              <tr>
                {/* 5건 밖에 유지하지 않을 예정이므로, 전체선택은 제외 */}
                <th scope="col">선택</th>
                <th scope="col">제목</th>
                <th scope="col">상태</th>
                <th scope="col">우선순위</th>
              </tr>
            </thead>

            <tbody>
              {
                conditionList.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="text-center" >자주 사용하는 조건이 없습니다.</td>
                  </tr>
                ) : (
                  conditionList.map((condition, _) => (
                    <tr style={{ height: '10px' }} className="align-middle">
                      <td><input type="checkbox"></input></td>
                      <td>{condition.title}</td>
                      <td>{condition.status}</td>
                      <td>{condition.priority}</td>
                    </tr>
                  ))
                )
              }
            </tbody>
          </table>

          <div className="text-end mt-4 me-3 d-grid gap-2 d-md-flex justify-content-md-end">
            <button className="btn btn-outline-danger btn-sm">선택 삭제</button>
            <button className="btn btn-outline-dark" onClick={onClose}>닫기</button>
            {/* 1건만 선택했을 때 적용 가능 */}
            <button className="btn btn-outline-primary" onClick={onApply}>적용</button>
          </div>

        </div>
        
      </div>
    </div>
    ,
    modalRoot
  );

}


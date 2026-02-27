type TodoReplyRegistProps = {
    onRegist: (content: string) => void;
};

export default function TodoReplyRegist({onRegist}: TodoReplyRegistProps) {
    return(
        <>
            <div className="comment-form">
                <div className="comment-form-header">✏️ 댓글 작성</div>
                <label>댓글 내용</label>
                <textarea id="newContent" placeholder="댓글을 입력하세요..."></textarea>
                <div className="comment-form-footer">
                    <button className="btn btn-comment" onClick={() => onRegist((document.getElementById('newContent')! as HTMLTextAreaElement).value)}>등록</button>
                </div>
            </div>
        </>
    );
}
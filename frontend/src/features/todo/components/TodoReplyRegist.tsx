import { useState } from "react";
import { toast } from 'react-toastify';

type TodoReplyRegistProps = {
    onRegist: (author : string, content: string) => void;
};

export default function TodoReplyRegist({onRegist}: TodoReplyRegistProps) {

    const [author, setAuthor] = useState('');
    const [content, setContent] = useState('');

     const handleRegist = () => {
        if (!author.trim()) {
            toast.error('답글 작성자가 비어있습니다.');
            return;
        }
        if (!content.trim()) {
            toast.error('답글 내용이 비어있습니다.');
            return;
        }
        onRegist(author, content);
        setAuthor('');
        setContent('');
    };

    return(
        <>
            <div className="comment-form">
                <div className="comment-form-header">✏️ 댓글 작성</div>
                <div className="comment-form-row">
                    <div>
                        <label>작성자</label>
                        <input type="text" 
                                placeholder="이름" 
                                value={author}
                                onChange={(e) => setAuthor(e.target.value)} />
                    </div>
                </div>
                <label>댓글 내용</label>
                <textarea 
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="댓글을 입력하세요..."
                />
                <div className="comment-form-footer">
                    <button className="btn btn-comment" onClick={handleRegist}>등록</button>
                </div>
            </div>
        </>
    );
}
'use client';

import { useState } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { studyApi } from '@/lib/api';
import { toast } from 'sonner';
import { Spinner } from '@/components/ui/spinner';
import { GraduationCap, Brain, BookOpen, Calendar, Check, X } from 'lucide-react';

export default function StudyPage() {
  const [activeTab, setActiveTab] = useState('quiz');

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold">Study Tools</h1>
          <p className="text-gray-500">Quizzes, flashcards, summaries, and study plans</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-4 w-full max-w-2xl">
            <TabsTrigger value="quiz">Quiz Generator</TabsTrigger>
            <TabsTrigger value="flashcards">Flashcards</TabsTrigger>
            <TabsTrigger value="summarize">Summarizer</TabsTrigger>
            <TabsTrigger value="planner">Study Planner</TabsTrigger>
          </TabsList>

          <TabsContent value="quiz" className="mt-6">
            <QuizGenerator />
          </TabsContent>

          <TabsContent value="flashcards" className="mt-6">
            <FlashcardGenerator />
          </TabsContent>

          <TabsContent value="summarize" className="mt-6">
            <NoteSummarizer />
          </TabsContent>

          <TabsContent value="planner" className="mt-6">
            <StudyPlanner />
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}

function QuizGenerator() {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [count, setCount] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [quiz, setQuiz] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setIsLoading(true);
    try {
      const res = await studyApi.generateQuiz({ topic, difficulty, question_count: count });
      setQuiz(res.data);
      setAnswers({});
      setResult(null);
    } catch {
      toast.error('Failed to generate quiz');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    try {
      const res = await studyApi.submitQuiz(quiz.id, answers);
      setResult(res.data);
    } catch {
      toast.error('Failed to submit quiz');
    }
  };

  const handleAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-1 block">Topic</label>
              <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g., Photosynthesis" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Difficulty</label>
              <Select value={difficulty} onValueChange={setDifficulty}>
                <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="easy">Easy</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="hard">Hard</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Questions</label>
              <Input type="number" min={5} max={50} value={count} onChange={(e) => setCount(parseInt(e.target.value) || 10)} className="w-20" />
            </div>
            <Button onClick={handleGenerate} disabled={isLoading || !topic.trim()}>
              {isLoading ? <Spinner size="sm" /> : <><Brain className="h-4 w-4 mr-2" /> Generate</>}
            </Button>
          </div>
        </CardContent>
      </Card>

      {quiz && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-primary-600" />
              {quiz.title}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {quiz.questions.map((q: any, i: number) => (
              <div key={q.id} className="border-b pb-4 last:border-0">
                <p className="font-medium mb-2">{i + 1}. {q.question_text}</p>
                {q.options && (
                  <div className="space-y-2">
                    {q.options.map((opt: string, j: number) => {
                      const letter = String.fromCharCode(65 + j);
                      const isSelected = answers[q.id] === letter;
                      const isCorrect = result && letter === q.correct_answer;
                      const isWrong = result && isSelected && letter !== q.correct_answer;

                      return (
                        <button
                          key={j}
                          onClick={() => !result && handleAnswer(q.id, letter)}
                          className={`w-full text-left p-3 rounded-lg border text-sm transition-colors ${
                            result
                              ? isCorrect
                                ? 'border-green-500 bg-green-50'
                                : isWrong
                                  ? 'border-red-500 bg-red-50'
                                  : 'border-gray-200'
                              : isSelected
                                ? 'border-primary-500 bg-primary-50'
                                : 'border-gray-200 hover:border-gray-300'
                          }`}
                          disabled={!!result}
                        >
                          <span className="font-medium mr-2">{letter}.</span>
                          {opt}
                        </button>
                      );
                    })}
                  </div>
                )}
                {result && q.explanation && (
                  <p className="text-sm text-gray-500 mt-2">{q.explanation}</p>
                )}
              </div>
            ))}

            {!result && (
              <Button onClick={handleSubmit} className="w-full" disabled={Object.keys(answers).length === 0}>
                Submit Answers
              </Button>
            )}
            {result && (
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-lg font-bold">{result.score}/{result.total_points} ({result.percentage}%)</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function FlashcardGenerator() {
  const [topic, setTopic] = useState('');
  const [count, setCount] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [flashcards, setFlashcards] = useState<any>(null);
  const [currentCard, setCurrentCard] = useState(0);
  const [flipped, setFlipped] = useState(false);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setIsLoading(true);
    try {
      const res = await studyApi.generateFlashcards({ topic, count });
      setFlashcards(res.data);
      setCurrentCard(0);
      setFlipped(false);
    } catch {
      toast.error('Failed to generate flashcards');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-1 block">Topic</label>
              <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g., World War II" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Count</label>
              <Input type="number" min={5} max={100} value={count} onChange={(e) => setCount(parseInt(e.target.value) || 10)} className="w-20" />
            </div>
            <Button onClick={handleGenerate} disabled={isLoading || !topic.trim()}>
              {isLoading ? <Spinner size="sm" /> : <><Brain className="h-4 w-4 mr-2" /> Generate</>}
            </Button>
          </div>
        </CardContent>
      </Card>

      {flashcards && flashcards.flashcards?.[currentCard] && (
        <div className="max-w-lg mx-auto">
          <div
            onClick={() => setFlipped(!flipped)}
            className="cursor-pointer min-h-[250px]"
          >
            <Card className={`p-8 text-center transition-all ${flipped ? 'bg-primary-50 border-primary-200' : ''}`}>
              <CardContent>
                <p className="text-sm text-gray-400 mb-4">
                  Card {currentCard + 1} of {flashcards.flashcards.length}
                </p>
                <p className="text-xl font-medium">
                  {flipped
                    ? flashcards.flashcards[currentCard].back
                    : flashcards.flashcards[currentCard].front}
                </p>
                <p className="text-xs text-gray-400 mt-6">
                  Click to {flipped ? 'see question' : 'reveal answer'}
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-center gap-4 mt-4">
            <Button variant="outline" onClick={() => { setCurrentCard(Math.max(0, currentCard - 1)); setFlipped(false); }} disabled={currentCard === 0}>
              Previous
            </Button>
            <Button variant="outline" onClick={() => { setCurrentCard(Math.min(flashcards.flashcards.length - 1, currentCard + 1)); setFlipped(false); }} disabled={currentCard === flashcards.flashcards.length - 1}>
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function NoteSummarizer() {
  const [text, setText] = useState('');
  const [format, setFormat] = useState('bullets');
  const [detailLevel, setDetailLevel] = useState('moderate');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSummarize = async () => {
    if (!text.trim()) return;
    setIsLoading(true);
    try {
      const res = await studyApi.summarize({ text, format, detail_level: detailLevel });
      setResult(res.data);
    } catch {
      toast.error('Failed to summarize notes');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="space-y-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="text-sm font-medium mb-1 block">Format</label>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="bullets">Bullet Points</SelectItem>
                <SelectItem value="paragraphs">Paragraphs</SelectItem>
                <SelectItem value="outline">Outline</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex-1">
            <label className="text-sm font-medium mb-1 block">Detail</label>
            <Select value={detailLevel} onValueChange={setDetailLevel}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="concise">Concise</SelectItem>
                <SelectItem value="moderate">Moderate</SelectItem>
                <SelectItem value="detailed">Detailed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full min-h-[300px] rounded-lg border border-gray-300 p-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Paste your notes here..."
        />
        <Button onClick={handleSummarize} className="w-full" disabled={isLoading || !text.trim()}>
          {isLoading ? <Spinner size="sm" /> : <><BookOpen className="h-4 w-4 mr-2" /> Summarize</>}
        </Button>
      </div>
      <div>
        {result ? (
          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
              <p className="text-xs text-gray-500">{result.original_length} chars → {result.summary_length} chars</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="prose-custom text-sm">{result.summary}</div>
              {result.key_points?.length > 0 && (
                <div>
                  <p className="font-medium text-sm mb-2">Key Points:</p>
                  <ul className="list-disc pl-4 space-y-1">
                    {result.key_points.map((kp: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600">{kp}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-[400px] text-gray-400">
              <BookOpen className="h-16 w-16 mb-4" />
              <p className="text-lg font-medium">Summary will appear here</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function StudyPlanner() {
  const [subject, setSubject] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [hoursPerDay, setHoursPerDay] = useState(2);
  const [isLoading, setIsLoading] = useState(false);
  const [plan, setPlan] = useState<any>(null);

  const handleGenerate = async () => {
    if (!subject.trim() || !startDate || !endDate) return;
    setIsLoading(true);
    try {
      const res = await studyApi.generateStudyPlan({
        subject,
        start_date: startDate,
        end_date: endDate,
        hours_per_day: hoursPerDay,
      });
      setPlan(res.data);
      toast.success('Study plan generated!');
    } catch {
      toast.error('Failed to generate study plan');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTask = (taskId: string) => {
    if (!plan) return;
    setPlan({
      ...plan,
      tasks: plan.tasks.map((t: any) =>
        t.id === taskId ? { ...t, is_completed: !t.is_completed } : t
      ),
    });
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-4">
          <div className="grid gap-4 md:grid-cols-5 items-end">
            <div>
              <label className="text-sm font-medium mb-1 block">Subject</label>
              <Input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="e.g., Biology" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Start Date</label>
              <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">End Date</label>
              <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Hours/Day</label>
              <Input type="number" min={0.5} max={12} step={0.5} value={hoursPerDay} onChange={(e) => setHoursPerDay(parseFloat(e.target.value) || 2)} />
            </div>
            <Button onClick={handleGenerate} disabled={isLoading}>
              {isLoading ? <Spinner size="sm" /> : <><Calendar className="h-4 w-4 mr-2" /> Generate Plan</>}
            </Button>
          </div>
        </CardContent>
      </Card>

      {plan && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary-600" />
              {plan.title}
            </CardTitle>
            <p className="text-sm text-gray-500">
              {new Date(plan.start_date).toLocaleDateString()} - {new Date(plan.end_date).toLocaleDateString()} | {plan.hours_per_day} hrs/day
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {plan.tasks.map((task: any) => (
                <div
                  key={task.id}
                  onClick={() => toggleTask(task.id)}
                  className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    task.is_completed ? 'bg-green-50 border-green-200' : 'hover:bg-gray-50'
                  }`}
                >
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    task.is_completed ? 'border-green-500 bg-green-500' : 'border-gray-300'
                  }`}>
                    {task.is_completed && <Check className="h-3 w-3 text-white" />}
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${task.is_completed ? 'line-through text-gray-400' : ''}`}>
                      {task.title}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(task.scheduled_date).toLocaleDateString()} | {task.duration_minutes} min
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
